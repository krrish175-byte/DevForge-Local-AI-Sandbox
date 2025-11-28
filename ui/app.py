import sys
import os

# --- Fix Import Path (Required for Streamlit) ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from engine.repair_loop import repair_code
import time

st.set_page_config(
    page_title="AutoPatch – Local AI Debugger",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Sidebar ----------------
st.sidebar.title("⚙️ Settings")
use_ai = st.sidebar.checkbox("Use Offline LLM (recommended)", value=False)
iterations = st.sidebar.slider("Max Repair Iterations", 1, 5, 3)

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Upload Python File", type=["py"])

# ---------------- Main UI ----------------
st.title(" AutoPatch — Local Autonomous Debugger")

st.markdown(
    "<p style='color:#BBBBBB; font-size:15px;'>Fully offline • Hybrid Rule-Based + AI • Secure Sandbox</p>",
    unsafe_allow_html=True,
)

st.markdown("### 📝 Enter your Python code")

if uploaded_file:
    code = uploaded_file.read().decode()
else:
    code = st.text_area(
        "Paste your Python code here:",
        height=250,
        placeholder="def hello():\n    print('Hello World!')\nhello()",
    )

# Run button
run_button = st.button("Run AutoPatch", type="primary")

# ---------------- Animation Section ----------------
def show_loading_animation():
    load_text = st.empty()
    bar = st.progress(0)

    for i in range(100):
        time.sleep(0.01)
        bar.progress(i + 1)
        if i < 30:
            load_text.text(" Analyzing errors...")
        elif i < 60:
            load_text.text(" Applying patch rules...")
        elif i < 90:
            load_text.text(" Checking LLM (if enabled)...")
        else:
            load_text.text(" Validating repaired code...")

    time.sleep(0.2)
    load_text.empty()

def animated_diff(before, after):
    before_lines = before.split("\n")
    after_lines = after.split("\n")

    st.markdown("#### Animated Code Diff")

    for b, a in zip(before_lines, after_lines):
        if b != a:
            st.markdown(f"<p style='color:#00FF00; font-family:monospace;'>+ {a}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:#999999; font-family:monospace;'>{a}</p>", unsafe_allow_html=True)
        time.sleep(0.03)

# ---------------- Handle Execution ----------------
if run_button:
    if not code.strip():
        st.error("Please enter some code before running AutoPatch.")
    else:

        # Run animation
        show_loading_animation()

        # Execute repair engine
        final_code, trace = repair_code(code, max_iterations=iterations, use_ai=use_ai)

        st.success("AutoPatch finished debugging!")

        # Confetti animation on success

        st.markdown("## Final Repaired Code")
        st.code(final_code, language="python")

        st.markdown("## Repair Trace (Step-by-Step)")

        for step in trace:
            with st.expander(f"Iteration {step.get('iteration')} — {step.get('message')}"):
                st.write(f"**Success:** {step.get('success')}")
                st.write(f"**Applied Rule / Source:** {step.get('rule')}")
                st.write(f"**Error Type:** {step.get('error_type', 'N/A')}")
                st.write(f"**Error Line:** {step.get('line', 'N/A')}")

                before = step.get("code_before", "")
                after = step.get("code_after", "")

                if before and after:
                    animated_diff(before, after)

                st.markdown("#### 📤 Stdout")
                st.code(step.get("stdout") or "—")

                st.markdown("#### ❗ Stderr")
                st.code(step.get("stderr") or "—")