import torch
from typing import Optional, Dict

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "Salesforce/codet5-small"
_tokenizer = None
_model = None
_device = None


def _load_model() -> bool:
    global _tokenizer, _model, _device

    if _tokenizer is not None and _model is not None:
        return True

    try:
        _device = torch.device("cpu")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        _model.to(_device)
        return True
    except Exception as e:
        print("LLM model load failed:", e)
        return False


def ai_suggest_patch(code: str, error: Dict) -> Optional[str]:
    """
    Uses CodeT5-small offline to fix Python code.
    Returns patched code OR None.
    """
    if not _load_model():
        return None

    # SAFE PROMPT (no backticks, no triple quotes inside)
    prompt = (
        "You are an AI that fixes Python code.\n"
        "Given the code and the error details, return ONLY the fixed Python code.\n"
        "Do not provide explanations.\n\n"
        "CODE:\n"
        f"{code}\n\n"
        "ERROR TYPE:\n"
        f"{error.get('error_type','')}\n\n"
        "ERROR MESSAGE:\n"
        f"{error.get('message','')}\n\n"
        "ERROR LINE:\n"
        f"{error.get('line','')}\n\n"
        "PROBLEMATIC LINE:\n"
        f"{error.get('code_line','')}\n\n"
        "Return only the corrected code below:\n"
    )

    try:
        inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(_device) for k, v in inputs.items()}

        output_ids = _model.generate(
            **inputs,
            max_length=256,
            num_beams=4,
            early_stopping=True,
        )

        result = _tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Sometimes LLM returns explanations → keep from first "def " if present
        if "def " in result:
            result = result[result.index("def ") :]

        result = result.strip()
        return result if result else None
    except Exception as e:
        print("LLM inference failed:", e)
        return None