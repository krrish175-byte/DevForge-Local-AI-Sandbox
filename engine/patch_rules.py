# engine/patch_rules.py

from typing import Dict, Tuple, Optional
import re
import textwrap

def fix_index_error(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "IndexError" not in err["error_type"]:
        return None, None

    # Common pattern: range(len(arr) + 1) -> range(len(arr))
    pattern = r"range\s*\(\s*len\((.*?)\)\s*\+\s*1\s*\)"
    new_code = re.sub(pattern, r"range(len(\1))", code)
    if new_code != code:
        return new_code, "fix_index_off_by_one"

    return None, None


def fix_zero_division(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "ZeroDivisionError" not in err["error_type"]:
        return None, None

    # Naive but fine: x / 0 -> x / 1
    pattern = r"(/)\s*0\b"
    new_code = re.sub(pattern, r"/ 1", code)
    if new_code != code:
        return new_code, "fix_zero_division"
    return None, None


def fix_type_error(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "TypeError" not in err["error_type"]:
        return None, None

    line = err.get("code_line", "")
    if "+" in line:
        # crude but works for many cases: a + b -> f"{a}{b}"
        new_line = re.sub(r"(.+)\+(.+)", r'f"{\1}{\2}"', line)
        new_code = code.replace(line, new_line)
        if new_code != code:
            return new_code, "fix_type_concat"
    return None, None


def fix_indentation_error(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "IndentationError" not in err["error_type"]:
        return None, None

    dedented = textwrap.dedent(code)
    return dedented, "fix_indentation"


def fix_recursion_error(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Add a simple base case to a recursive function:
        if n <= 0: return 0
    This is a heuristic, but great for demo.
    """
    if "RecursionError" not in err["error_type"]:
        return None, None

    lines = code.split("\n")
    func_name = None
    func_line_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def ") and "(" in stripped and ")" in stripped:
            func_name = stripped.split("def ")[1].split("(")[0]
            func_line_idx = i
            break

    if func_name is None:
        return None, None

    # Insert base case after def line
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if i == func_line_idx:
            indent = " " * (len(line) - len(line.lstrip()) + 4)
            new_lines.append(f"{indent}if n <= 0: return 0  # AutoPatch base case")

    new_code = "\n".join(new_lines)
    if new_code != code:
        return new_code, "fix_recursion_basecase"
    return None, None


RULES = [
    fix_index_error,
    fix_zero_division,
    fix_type_error,
    fix_indentation_error,
    fix_recursion_error,
]


def apply_rules(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    for rule in RULES:
        new_code, name = rule(code, err)
        if new_code is not None:
            return new_code, name
    return None, None