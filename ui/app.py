# ui/app.py

import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.repair_loop import repair_code  # noqa: E402

st.set_page_config(page_title="AutoPatch", layout="wide")

st.title("AutoPatch 🔧 Local Autonomous Debugger")
st.write(
    "Paste or upload Python code. AutoPatch will run it in a sandbox, "
    "observe errors, apply rule-based fixes, and optionally try an offline LLM "
    "(DeepSeek Coder 1.3B) for harder bugs."
)

file = st.file_uploader("Upload a .py file", type=["py"])

default_code = """def buggy(n):
    return buggy(n - 1)

print(buggy(3))
"""

if file:
    code_input = file.read().decode("utf-8")
else:
    code_input = st.text_area("Paste your Python code:", default_code, height=260)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    iterations = st.slider("Max repair iterations", 1, 10, 3)
with col2:
    use_ai = st.checkbox("Use AI (DeepSeek, offline)", value=True)
with col3:
    run = st.button("Run AutoPatch")

if run:
    st.info("Running in sandbox...")
    final_code, trace = repair_code(
        code_input,
        max_iterations=iterations,
        use_ai=use_ai,
    )

    st.subheader("Repair Trace")
    for step in trace:
        title = f"Iteration {step.get('iteration')} – {step.get('message')}"
        with st.expander(title, expanded=True):
            st.write(
                f"Success: {step.get('success')} | "
                f"Patched: {step.get('patched')} | "
                f"Source: {step.get('source')} | "
                f"Rule/Model: {step.get('rule')}"
            )
            if step.get("stderr"):
                st.code(step["stderr"], language="text")
            if step.get("diff"):
                st.code(step["diff"], language="diff")

    st.subheader("Final Repaired Code")
    st.code(final_code, language="python")