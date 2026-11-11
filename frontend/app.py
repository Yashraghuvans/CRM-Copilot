import os

import requests
import streamlit as st

API = os.environ.get("API_URL", "http://localhost:8000")
st.title("CRM-Copilot")

roles = requests.get(f"{API}/roles", timeout=10).json()
role = st.sidebar.selectbox("Role", list(roles))
user = st.sidebar.selectbox("User", roles[role], format_func=lambda u: u["name"])

key = (role, user["id"])
if st.session_state.get("key") != key:  # switching identity starts a fresh chat
    st.session_state.update(key=key, chat=[])

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.write(m["text"])
        if m.get("sources"):
            with st.expander("Sources"):
                st.write(m["sources"])

if query := st.chat_input("Ask CRM-Copilot"):
    st.session_state.chat.append({"role": "user", "text": query})
    r = requests.post(f"{API}/ask", json={"role": role, "user_id": user["id"], "query": query}, timeout=60)
    if r.ok:
        st.session_state.chat.append({"role": "assistant", "text": r.json()["answer"], "sources": r.json()["sources"]})
    else:
        st.session_state.chat.append({"role": "assistant", "text": f"Error {r.status_code}: {r.text}"})
    st.rerun()
