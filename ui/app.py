import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from engine.repair_loop import repair_code

st.set_page_config(page_title="AutoPatch", layout="wide")

st.title("AutoPatch – Local Autonomous Debugging System")
st.write("Upload code or paste manually, then click **Run AutoPatch**.")

file = st.file_uploader("Upload .py file", type=["py"])

default_code = """def buggy():
    arr = [1, 2, 3]
    for i in range(len(arr) + 1):
        print(arr[i])

buggy()
"""

if file:
    code_input = file.read().decode("utf-8")
else:
    code_input = st.text_area("Paste your Python code:", default_code, height=280)

iterations = st.slider("Max repair iterations", 1, 10, 5)

if st.button("Run AutoPatch"):
    st.subheader("Running AutoPatch...")

    with st.spinner("Executing in sandbox, analyzing errors, generating patches..."):
        final_code, trace = repair_code(code_input, max_iterations=iterations)

    st.success("Done.")

    st.header("Repair Trace")
    for step in trace:
        with st.expander(f"Iteration {step['iteration']}: {step['message']}"):
            st.write("**Success:**", step["success"])
            st.write("**Patch source:**", step["patch_source"])
            st.write("**Rule:**", step["rule"])
            st.write("**Patched:**", step["patched"])
            st.write("**Error object:**", step["error"])
            st.write("**Stdout:**")
            st.code(step.get("stdout") or "")
            st.write("**Stderr:**")
            st.code(step.get("stderr") or "")
            if step.get("diff"):
                st.write("**Patch diff:**")
                st.code(step["diff"], language="diff")

    st.header("Final Repaired Code")
    st.code(final_code, language="python")