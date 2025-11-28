# engine/repair_loop.py

from __future__ import annotations

from typing import Dict, List, Tuple
import difflib
import ast

from .sandbox_runner import run_code
from .error_parser import parse_traceback
from .patch_rules import apply_rules
from .llm_patch import ai_suggest_patch


def _diff(a: str, b: str, label: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            a.splitlines(),
            b.splitlines(),
            fromfile="before",
            tofile=f"after ({label})",
            lineterm="",
        )
    )


def _is_valid_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def repair_code(
    initial_code: str,
    max_iterations: int = 5,
    use_ai: bool = False,
) -> Tuple[str, List[Dict]]:
    """
    Run → Observe → Patch → Apply → Run loop.
    Returns final_code and a list of trace steps.
    """
    code = initial_code
    trace: List[Dict] = []

    for i in range(1, max_iterations + 1):
        success, stdout, stderr = run_code(code)

        step: Dict = {
            "iteration": i,
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "patched": False,
            "source": None,      # "rule" or "llm"
            "rule": None,
            "message": "",
            "diff": None,
        }

        if success:
            step["message"] = "Code ran successfully. Stopping."
            trace.append(step)
            return code, trace

        err = parse_traceback(stderr, code)
        if not err:
            step["message"] = "Could not parse error. Stopping."
            trace.append(step)
            return code, trace

        # 1) Try rules
        new_code, rule_name = apply_rules(code, err)
        if new_code and new_code.strip() != code.strip():
            if _is_valid_python(new_code):
                step["patched"] = True
                step["source"] = "rule"
                step["rule"] = rule_name
                step["message"] = f"Applied rule: {rule_name}"
                step["diff"] = _diff(code, new_code, f"rule:{rule_name}")
                trace.append(step)
                code = new_code
                continue
            else:
                step["message"] = f"Rule {rule_name} produced invalid code, ignoring."
                trace.append(step)
                # fall-through to LLM if enabled

        # 2) Try LLM if enabled
        if use_ai:
            ai_code = ai_suggest_patch(code, err)
            if ai_code and ai_code.strip() != code.strip():
                if _is_valid_python(ai_code):
                    step["patched"] = True
                    step["source"] = "llm"
                    step["rule"] = "deepseek_coder_1.3b"
                    step["message"] = "Applied LLM-generated patch."
                    step["diff"] = _diff(code, ai_code, "llm:deepseek")
                    trace.append(step)
                    code = ai_code
                    continue
                else:
                    step["message"] = "LLM produced invalid Python. Stopping."
                    step["source"] = "llm_invalid"
                    trace.append(step)
                    return code, trace
            else:
                step["message"] = "LLM could not generate a better patch. Stopping."
                step["source"] = "llm_failed"
                trace.append(step)
                return code, trace

        # No rules, AI disabled
        step["message"] = "No applicable rule, and AI disabled."
        trace.append(step)
        return code, trace

    trace.append(
        {
            "iteration": max_iterations + 1,
            "success": False,
            "message": "Reached max iterations.",
            "patched": False,
            "source": None,
            "rule": None,
            "stdout": "",
            "stderr": "",
            "diff": None,
        }
    )
    return code, trace