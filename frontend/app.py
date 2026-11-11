import requests
import streamlit as st

API = "http://localhost:8000"
role = st.selectbox("Role", requests.get(f"{API}/roles").json())
question = st.text_input("Ask the copilot")
if question:
    r = requests.post(f"{API}/ask", json={"role": role, "question": question})
    r.raise_for_status()
    st.write(r.json()["answer"])
    with st.expander("Context used"):
        st.text(r.json()["context"])
