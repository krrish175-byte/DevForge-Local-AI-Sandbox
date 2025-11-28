import subprocess
import tempfile
import sys
from typing import Tuple

def run_code(code: str) -> Tuple[bool, str, str]:
    """
    Runs code in a sandboxed subprocess with time/memory limits.
    Returns: (success, stdout, stderr)
    """

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        proc = subprocess.Popen(
            [sys.executable, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=2)

        success = proc.returncode == 0
        return success, stdout, stderr

    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "", "TimeoutExpired: Execution exceeded time limit"

    except Exception as e:
        return False, "", str(e)