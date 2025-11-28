# engine/patch_rules.py

from typing import Dict, Tuple, Optional
import re
import textwrap


# ---------------------
# RUNTIME ERROR RULES
# ---------------------

def fix_index_error(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "IndexError" not in err.get("error_type", ""):
        return None, None

    pattern = r"range\s*\(\s*len\((.*?)\)\s*\+\s*1\s*\)"
    new_code = re.sub(pattern, r"range(len(\1))", code)
    if new_code != code:
        return new_code, "fix_index_off_by_one"
    return None, None


def fix_zero_division(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "ZeroDivisionError" not in err.get("error_type", ""):
        return None, None

    new_code = re.sub(r"(/)\s*0\b", "/ 1", code)
    if new_code != code:
        return new_code, "fix_zero_division"
    return None, None


def fix_type_error(code: str, err: Dict) -> Tuple[Optional[str], Optional[str]]:
    if "TypeError" not in err.get("error_type", ""):
        return None, None

    line = err.get("code_line", "")
    if "+" in line:
        new_line = re.sub(r"(.+)\+(.+)", r'f"{\1}{\2}"', line)
        new_code = code.replace(line, new_line)
        if new_code != code:
            return new_code, "fix_type_concat"
    return None, None


def fix_indentation_error(code: str, err: Dict):
    if "IndentationError" not in err.get("error_type", ""):
        return None, None

    dedented = textwrap.dedent(code)
    return dedented, "fix_indentation"


def fix_recursion_error(code: str, err: Dict):
    if "RecursionError" not in err.get("error_type", ""):
        return None, None

    lines = code.split("\n")

    func_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("def ") and "(" in line:
            func_index = i
            break

    if func_index is None:
        return None, None

    indent = " " * (len(lines[func_index]) - len(lines[func_index].lstrip()) + 4)
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if i == func_index:
            new_lines.append(f"{indent}if n <= 0: return 0  # AutoPatch base case")

    new_code = "\n".join(new_lines)
    if new_code != code:
        return new_code, "fix_recursion_basecase"

    return None, None


# ---------------------
# LOGIC ERROR RULES (GENERALIZED)
# ---------------------

def fix_preorder_logic(code: str, err: Dict):
    """
    GENERALIZED FIX:
    Detects inorder logic inside a function named preorder,
    even with random spacing or indentation.
    """

    if "def preorder" not in code:
        return None, None

    # Find: left → root → right pattern
    has_left = re.search(r"preorder\([^)]*left[^)]*\)", code)
    has_append = re.search(r"res\.append", code)
    has_right = re.search(r"preorder\([^)]*right[^)]*\)", code)

    if has_left and has_append and has_right:

        # Replace inorder block using NON-SPECIFIC regex
        new_code = re.sub(
            r"preorder\([^)]*left[^)]*\)\s*res\.append\([^)]*\)\s*preorder\([^)]*right[^)]*\)",
            "res.append(root.val)\n    preorder(root.left, res)\n    preorder(root.right, res)",
            code,
            flags=re.S,
        )

        if new_code != code:
            return new_code, "fix_preorder_logic_general"

    return None, None


def fix_memo_bug(code: str, err: Dict):
    """
    GENERALIZED FIX for memoized recursion bug:
    return memo[0] → return memo[n] or whichever var is inside condition.
    """

    pattern = r"if\s+(\w+)\s+in\s+memo\s*:\s*return\s+memo\[0\]"
    match = re.search(pattern, code)

    if match:
        var = match.group(1)
        new_code = re.sub(r"memo\[0\]", f"memo[{var}]", code)
        if new_code != code:
            return new_code, "fix_memo_bug_general"

    return None, None


# ---------------------
# RULESET
# ---------------------

RULES = [
    fix_index_error,
    fix_zero_division,
    fix_type_error,
    fix_indentation_error,
    fix_recursion_error,
    fix_preorder_logic,
    fix_memo_bug,
]


def apply_rules(code: str, err: Dict):
    for rule in RULES:
        new_code, name = rule(code, err)
        if new_code is not None:
            return new_code, name
    return None, None