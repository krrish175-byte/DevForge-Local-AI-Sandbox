import os
from engine.repair_loop import repair_code

tests = "tests/"

files = [f for f in os.listdir(tests) if f.endswith(".py")]
print(f"Found {len(files)} test files in tests\n")

for f in files:
    print(f"=== Running {f} ===")
    code = open(os.path.join(tests, f)).read()

    final, trace = repair_code(code, max_iterations=5)

    last = trace[-1]
    print("Final status:", "SUCCESS" if last["success"] else "FAILED")
    print("Message:", last["message"])
    print("")