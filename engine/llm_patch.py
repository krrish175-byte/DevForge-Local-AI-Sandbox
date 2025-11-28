# engine/llm_patch.py

from __future__ import annotations

from typing import Dict, Optional
import os
import ast

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None  # will handle gracefully

_LLM: Optional[Llama] = None

DEFAULT_MODEL_PATH = "models/deepseek-coder-1.3b-instruct.Q4_K_M.gguf"


def _get_llm() -> Optional[Llama]:
    """
    Lazy-load the local GGUF model. Returns None if unavailable.
    """
    global _LLM
    if _LLM is not None:
        return _LLM

    if Llama is None:
        print("[LLM] llama_cpp not installed; skipping LLM.")
        return None

    model_path = os.getenv("AUTOPATCH_LLM_PATH", DEFAULT_MODEL_PATH)
    if not os.path.exists(model_path):
        print(f"[LLM] Model file not found: {model_path}")
        return None

    try:
        print(f"[LLM] Loading model from {model_path} ...")
        _LLM = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=4,  # adjust based on CPU cores
        )
        print("[LLM] Model loaded.")
        return _LLM
    except Exception as e:
        print(f"[LLM] Failed to load model: {e}")
        return None


def ai_suggest_patch(code: str, err: Dict) -> Optional[str]:
    """
    Use local LLM to generate a FULL fixed version of the script.
    Returns None if LLM is unavailable or output invalid.
    """
    llm = _get_llm()
    if llm is None:
        return None

    error_type = err.get("error_type", "UnknownError")
    line = err.get("line")
    code_line = (err.get("code_line") or "").strip()

    prompt = f"""
You are an expert Python debugging assistant.

You are given a Python script and an error that occurred when running it.

Your job:
- Fix the bug.
- Return ONLY the corrected full Python script.
- Do NOT add explanations or comments.
- Do NOT wrap code in backticks.

Error:
- Type: {error_type}
- Line: {line}
- Code: {code_line}

### Broken script:
{code}

### Fixed script (only code):
"""

    try:
        result = llm(
            prompt,
            max_tokens=512,
            temperature=0.1,
            stop=["### Broken script:", "### Fixed script"],
        )
        text = result["choices"][0]["text"].strip()

        if not text:
            print("[LLM] Empty output, ignoring.")
            return None

        # Validate Python syntax
        try:
            ast.parse(text)
        except SyntaxError:
            print("[LLM] Generated invalid Python, ignoring.")
            return None

        return text

    except Exception as e:
        print(f"[LLM] Generation error: {e}")
        return None