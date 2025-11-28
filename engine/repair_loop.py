from .sandbox_runner import run_code
from .error_parser import parse_traceback
from .patch_rules import apply_rules

def repair_code(initial_code: str, max_iterations: int = 3):
    code = initial_code
    trace = []

    for i in range(1, max_iterations + 1):
        success, stdout, stderr = run_code(code)

        step = {
            "iteration": i,
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "patched": False,
            "patch_source": None,
            "rule": None
        }

        if success:
            step["message"] = "Code ran successfully, stopping."
            trace.append(step)
            return code, trace

        error = parse_traceback(stderr, code)
        step["error"] = error

        if not error:
            step["message"] = "Could not parse error, stopping."
            trace.append(step)
            return code, trace

        new_code, rule_name = apply_rules(code, error)

        if not new_code:
            step["message"] = "No rule matched. Stopping."
            trace.append(step)
            return code, trace

        step["patched"] = True
        step["patch_source"] = "RULE"
        step["rule"] = rule_name
        code = new_code
        trace.append(step)

    return code, trace