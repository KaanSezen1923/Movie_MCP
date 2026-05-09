import streamlit as st
import time
import requests
import uuid
import json

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
    
def display_message(role, content):
    with st.chat_message(role):
        if role == "assistant":
            try:
                # Metin JSON mı diye kontrol et
                data = json.loads(content)
                if isinstance(data, dict) and data.get("type") == "movie_list":
                    st.write(data.get("text", ""))
                    if data.get("movies"):
                        for movie in data["movies"]:
                            with st.expander(f"🎬 {movie.get('Film', 'Bilinmeyen Film')} ({movie.get('Yıl', 'N/A')})"):
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    poster_url = movie.get("Poster")
                                    if poster_url and poster_url != "URL":
                                        st.image(poster_url, width=150)
                                    else:
                                        st.write("Poster Yok")
                                with col2:
                                    st.markdown(f"**IMDb:** {movie.get('IMDb', 'N/A')}")
                                    st.markdown(f"**Türler:** {movie.get('Türler', 'N/A')}")
                                    st.markdown(f"**Platform:** {movie.get('Şu Anki Platform(lar)', 'N/A')}")
                                    st.markdown(f"**Özet:** {movie.get('Özet', 'N/A')}")
                                    fragman_url = movie.get("Fragman")
                                    if fragman_url and fragman_url != "URL":
                                        st.markdown(f"[🎥 Fragman İzle]({fragman_url})")
                    return
            except (json.JSONDecodeError, TypeError):
                pass # JSON değilse normal metin olarak devam et
        
        # Eğer user mesajıysa veya JSON değilse düz yazdır
        st.write(content)

def get_sessions(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/sessions/{user_id}")
        if response.status_code == 200:
            return response.json().get("sessions", [])
    except:
        pass
    return []

def get_chat_history(user_id, session_id):
    try:
        response = requests.get(f"{API_BASE_URL}/chat/{user_id}/{session_id}")
        if response.status_code == 200:
            return response.json().get("history", [])
    except:
        pass
    return []

def delete_session(user_id, session_id):
    try:
        requests.delete(f"{API_BASE_URL}/chat/{user_id}/{session_id}")
    except:
        pass

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
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Yeni Sohbet", use_container_width=True):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []
        st.rerun()
        
    if col2.button("Çıkış Yap", use_container_width=True):
        del st.session_state["user_id"]
        if "session_id" in st.session_state:
            del st.session_state["session_id"]
        st.session_state["messages"] = []
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("Geçmiş Sohbetler")
    sessions = get_sessions(st.session_state['user_id'])
    for session in sessions:
        sess_id = session["session_id"]
        title = session["title"]
        if len(title) > 25:
            title = title[:23] + "..."
            
        col_chat, col_del = st.sidebar.columns([4, 1])
        if col_chat.button(title, key=f"chat_{sess_id}", use_container_width=True):
            st.session_state["session_id"] = sess_id
            st.session_state["messages"] = get_chat_history(st.session_state["user_id"], sess_id)
            st.rerun()
        if col_del.button("🗑️", key=f"del_{sess_id}", help="Sohbeti sil"):
            delete_session(st.session_state["user_id"], sess_id)
            if st.session_state.get("session_id") == sess_id:
                st.session_state["session_id"] = str(uuid.uuid4())
                st.session_state["messages"] = []
            st.rerun()

    st.title("🎬 Movie MCP Chat")

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Chat geçmişini ekrana bas
    for msg in st.session_state["messages"]:
        display_message(msg["role"], msg["content"])
    user_input = st.chat_input("Bugün ne izlemek istersin?")
    if user_input:
        # Kullanıcı mesajı
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        start_time = time.time()
        with st.spinner("Film danışmanınız düşüniyor..."):
            answer = ask_mcp(user_input, st.session_state["session_id"])
        
        # JSON'u parse et
        try:
            data = json.loads(answer)
        except json.JSONDecodeError:
            data = {"type": "error", "text": answer, "movies": []}
        
        # Asistan yanıtı
        display_message("assistant", answer)
                          
        
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        
        end_time = time.time()
        st.caption(f"⏱️ Cevap süresi: {end_time - start_time:.2f} saniye")