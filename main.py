# main.py

import argparse
from pathlib import Path
from engine.repair_loop import repair_code

def main():
    parser = argparse.ArgumentParser(description="AutoPatch - Local Debugging Sandbox")
    parser.add_argument("file", help="Path to the Python file to debug")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Enable offline LLM (DeepSeek Coder 1.3B) for patching",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}")
        return

    code = path.read_text()
    final_code, trace = repair_code(
        code,
        max_iterations=args.iterations,
        use_ai=args.use_ai,
    )

    print("=== Repair Trace ===")
    for step in trace:
        print(f"\n--- Iteration {step.get('iteration')} ---")
        print("Success:", step.get("success"))
        print("Patched:", step.get("patched"), "Source:", step.get("source"))
        print("Rule/Model:", step.get("rule"))
        print("Message:", step.get("message"))
        print("Stderr:\n", step.get("stderr", ""))

    print("\n=== Final Repaired Code ===\n")
    print(final_code)

if __name__ == "__main__":
    main()