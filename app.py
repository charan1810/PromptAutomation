import streamlit as st
from prompt_multi_tables import generate_prompts_from_pdf
import io

st.set_page_config(page_title="Prompt Generator (PDF → Questions)", layout="wide")
st.title("Prompt Generator")

st.markdown("""
Upload a PDF that describes your schema/metrics/relationships/business rules.
I'll generate **only** natural-language question prompts.
""")

uploaded = st.file_uploader("Upload schema PDF", type=["pdf"])

# Session state
if "prompts" not in st.session_state:
    st.session_state.prompts = []

col1, col2 = st.columns([1,1])
with col1:
    gen = st.button("Generate Prompts", use_container_width=True, disabled=(uploaded is None))
with col2:
    reset = st.button("Reset", use_container_width=True)

if reset:
    st.session_state.prompts = []
    st.rerun()

if gen and uploaded is not None:
    with st.spinner("Reading PDF and generating prompts..."):
        prompts = generate_prompts_from_pdf(uploaded)   # <--- direct file handle
        st.session_state.prompts = prompts


if st.session_state.prompts:
    st.subheader(f"Generated Prompts ({len(st.session_state.prompts)})")
    for i, p in enumerate(st.session_state.prompts, 1):
        st.markdown(f"{i}. {p}")

    # Download as txt
    txt_bytes = io.BytesIO(("\n".join(st.session_state.prompts)).encode("utf-8"))
    st.download_button(
        label="Download Prompts (.txt)",
        data=txt_bytes,
        file_name="generated_prompts.txt",
        mime="text/plain",
    )

