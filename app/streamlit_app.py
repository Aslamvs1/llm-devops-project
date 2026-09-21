import os

import requests
import streamlit as st


st.set_page_config(
    page_title="Qwen AI Chat",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Qwen AI Chat")
st.caption("Self-hosted LLM • FastAPI • vLLM • AWS EKS • CI/CD")

FASTAPI_URL = os.getenv(
    "FASTAPI_URL",
    "http://localhost:8001",
)

prompt = st.text_area(
    "Message",
    placeholder="Ask something...",
    height=120,
)

if st.button("🚀 Send") and prompt.strip():
    try:
        with st.spinner("Qwen is thinking..."):
            response = requests.post(
                f"{FASTAPI_URL}/chat",
                json={"prompt": prompt.strip()},
                timeout=120,
            )

        response.raise_for_status()

        data = response.json()

        st.markdown("### 💬 Response")
        st.write(data["response"])

    except requests.exceptions.RequestException as error:
        st.error("Could not connect to FastAPI.")
        st.caption(str(error))