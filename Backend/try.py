import requests
import streamlit as st
import time 
import uuid

st.set_page_config(page_title="Movie MCP", page_icon="🎬")

API_BASE_URL = "http://localhost:8000"


def ask_mcp(prompt, session_id):
    # session_state içindeki user_id'yi gönderiyoruz
    payload = {
        "prompt": prompt,
        "user_id": st.session_state["user_id"],
        "session_id": session_id
    }
    response = requests.post("http://localhost:8000/chat", json=payload)
    if response.status_code == 200:
        return response.json().get("answer", "Cevap alınamadı.")
    else:
        return f"Hata: {response.status_code}"
    



if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Chat geçmişini ekrana bas
for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


user_input = st.chat_input("Bugün ne izlemek istersin?")

if user_input:
        # Kullanıcı mesajı
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        start_time = time.time()
        with st.spinner("Film danışmanınız düşüniyor..."):
            answer = ask_mcp(user_input, st.session_state["session_id"])
        
        # Asistan yanıtı
        with st.chat_message("assistant"):
            st.write(answer["movies"])
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        
        end_time = time.time()
        st.caption(f"⏱️ Cevap süresi: {end_time - start_time:.2f} saniye")

