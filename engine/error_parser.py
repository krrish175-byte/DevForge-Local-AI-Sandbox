# engine/error_parser.py

from typing import Dict, Optional
import re

def parse_traceback(stderr: str, code: str) -> Optional[Dict]:
    """
    Extract:
      - error_type
      - message
      - line number
      - code line
    from a Python traceback.
    """
    if not stderr or "Traceback" not in stderr:
        return None

    lines = stderr.strip().split("\n")

    # Last line is usually: "<ErrorType>: message"
    last = lines[-1]
    if ":" in last:
        error_type = last.split(":", 1)[0].strip()
        message = last.split(":", 1)[1].strip()
    else:
        error_type = last.strip()
        message = ""

    # Find last "File ... line X" entry
    line_num = None
    for line in reversed(lines):
        if "File " in line and "line " in line:
            m = re.search(r"line\s+(\d+)", line)
            if m:
                line_num = int(m.group(1))
                break

    if line_num is None:
        return {
            "error_type": error_type,
            "message": message,
            "line": None,
            "code_line": None,
        }

    code_lines = code.split("\n")
    if 1 <= line_num <= len(code_lines):
        code_line = code_lines[line_num - 1]
    else:
        code_line = ""

    return {
        "error_type": error_type,
        "message": message,
        "line": line_num,
        "code_line": code_line,
    }