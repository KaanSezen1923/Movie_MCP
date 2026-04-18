import streamlit as st
import time
import requests

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Movie MCP", page_icon="🎬")

API_BASE_URL = "http://localhost:8000"

# --- Giriş / Kayıt Fonksiyonları ---

def login_ui():
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı", key="login_user")
    password = st.text_input("Şifre", type="password", key="login_pw")
    if st.button("Giriş Yap", use_container_width=True):
        try:
            response = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                st.session_state["user_id"] = data["user_id"]
                st.session_state["username"] = data["username"]
                st.success(f"Hoş geldin {data['username']}!")
                st.rerun()
            else:
                st.error("Giriş başarısız. Bilgileri kontrol edin.")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")

def signup_ui():
    st.subheader("Kayıt Ol")
    new_user = st.text_input("Kullanıcı Adı", key="signup_user")
    new_email = st.text_input("E-posta", key="signup_email")
    new_pw = st.text_input("Şifre", type="password", key="signup_pw")
    if st.button("Kayıt Ol", use_container_width=True):
        try:
            response = requests.post(f"{API_BASE_URL}/signup", 
                                     json={"username": new_user, "email": new_email, "password": new_pw})
            if response.status_code == 200:
                st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
            else:
                detail = response.json().get("detail", "Kayıt hatası.")
                st.error(f"Hata: {detail}")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")

# --- Chat Fonksiyonu ---

def ask_mcp(prompt):
    # session_state içindeki user_id'yi gönderiyoruz
    payload = {
        "prompt": prompt,
        "user_id": st.session_state["user_id"] 
    }
    response = requests.post("http://localhost:8000/chat", json=payload)
    if response.status_code == 200:
        return response.json().get("answer", "Cevap alınamadı.")
    else:
        return f"Hata: {response.status_code}"

# --- Sayfa Akış Yönetimi ---

if "user_id" not in st.session_state:
    # Kullanıcı giriş yapmamışsa sadece Login/Signup göster
    st.title("🎬 Movie MCP'ye Hoş Geldiniz")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab1:
        login_ui()
    with tab2:
        signup_ui()
else:
    # Kullanıcı giriş yapmışsa Chat arayüzünü göster
    st.sidebar.title(f"👤 {st.session_state['username']}")
    if st.sidebar.button("Çıkış Yap"):
        del st.session_state["user_id"]
        st.session_state["messages"] = [] # Çıkış yapınca geçmişi temizle
        st.rerun()

    st.title("🎬 Movie MCP Chat")

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
            answer = ask_mcp(user_input)
        
        # Asistan yanıtı
        with st.chat_message("assistant"):
            st.write(answer)
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        
        end_time = time.time()
        st.caption(f"⏱️ Cevap süresi: {end_time - start_time:.2f} saniye")
