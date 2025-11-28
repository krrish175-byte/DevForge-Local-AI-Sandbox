# engine/sandbox_runner.py

import subprocess
import tempfile

def run_code(code: str):
    """
    Run code in an isolated subprocess using a temp file.
    Returns: (success, stdout, stderr)
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return proc.returncode == 0, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TimeoutExpired: execution took too long\n"
    except Exception as e:
        return False, "", f"Sandbox error: {e}\n"