import argparse
from pathlib import Path
from engine.repair_loop import repair_code

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--iterations", type=int, default=3)
    a = parser.parse_args()

    code = Path(a.file).read_text()

    final_code, trace = repair_code(code, max_iterations=a.iterations)

    print("=== Repair trace ===")
    for step in trace:
        print(f"\n--- Iteration {step['iteration']} ---")
        for k, v in step.items():
            print(f"{k}: {v}")

    print("\n=== Final repaired code ===")
    print(final_code)

if __name__ == "__main__":
    main()