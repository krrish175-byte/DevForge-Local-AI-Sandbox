import traceback
from typing import Dict, Optional

def parse_traceback(stderr: str, code: str) -> Optional[Dict]:
    """
    Extracts:
    - error_type
    - line number
    - code line
    """

    if not stderr:
        return None

    lines = stderr.strip().split("\n")
    error_type = lines[-1].split(":")[0].strip()

    # Find "line X"
    line_num = None
    for line in lines:
        if "line " in line:
            try:
                line_num = int(line.split("line")[1].split(",")[0])
            except:
                pass

    if line_num is None:
        return None

    code_lines = code.split("\n")
    if 1 <= line_num <= len(code_lines):
        code_line = code_lines[line_num - 1]
    else:
        code_line = ""

    return {
        "error_type": error_type,
        "line": line_num,
        "code_line": code_line
    }