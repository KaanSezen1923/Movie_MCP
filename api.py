import os
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI, HTTPException,BackgroundTasks
from pydantic import BaseModel,EmailStr, field_validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from client import get_ollama_tools, chat_with_session,generate_user_profile
import psycopg2
import bcrypt

load_dotenv()

class AppContext:
    def __init__(self):
        self.session = None
        self.tools = None
        self.exit_stack = AsyncExitStack()

ctx = AppContext()

@asynccontextmanager
async def lifespan(app: FastAPI):
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env={"AUTH_KEY": os.getenv("AUTH_KEY")}
    )

    print("🚀 MCP Sunucusu başlatılıyor...")
    try:
        # stdio_client'ı ExitStack ile güvenli başlatıyoruz
        read, write = await ctx.exit_stack.enter_async_context(stdio_client(server_params))
        
        ctx.session = await ctx.exit_stack.enter_async_context(ClientSession(read, write))
        await ctx.session.initialize()
        
        # Tool'ları çekiyoruz
        ctx.tools = await get_ollama_tools(ctx.session)
        print("✅ MCP Bağlantısı ve Toollar hazır!")
    except Exception as e:
        print(f"❌ Başlatma hatası: {e}")
        raise e
    
    yield
    
    # Kapanırken her şeyi otomatik temizler
    await ctx.exit_stack.aclose()
    print("🛑 MCP Bağlantısı kapatıldı.")

app = FastAPI(title="Movie Explorer AI API", lifespan=lifespan)


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )


class UserSignup(BaseModel):
    username: str
    email: EmailStr # Email formatı kontrolü yapar
    password: str

    @field_validator('password')
    @classmethod
    def truncate_password(cls, v: str) -> str:
        # Bcrypt 72 byte sınırı için 71'de kesiyoruz
        return v[:71]

class UserLogin(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    prompt: str
    user_id: int
    session_id: str

class ChatResponse(BaseModel):
    answer: str

def hash_password(password: str):
    # Şifreyi byte formatına çevirip hashliyoruz
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8') # Veritabanına string olarak kaydetmek için

def verify_password(plain_password, hashed_password):
    # plain_password: Kullanıcıdan gelen düz metin
    # hashed_password: Veritabanından gelen hashli metin
    password_byte = plain_password.encode('utf-8')
    hashed_byte = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte, hashed_byte)

def save_chat_to_db(user_id: int, role: str, content: str, session_id: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, content, session_id) VALUES (%s, %s, %s, %s)",
            (user_id, role, content, session_id)
        )
        conn.commit()
    except Exception as e:
        print(f"❌ DB Kayıt Hatası: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

def get_user_persona(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT persona_summary FROM user_profiles WHERE user_id = %s",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_recent_chats(user_id: int, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Son 10 mesajı al (kullanıcı ve asistan ikilisi şeklinde)
    cursor.execute(
        "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit)
    )
    chats = cursor.fetchall()
    conn.close()
    # Metin haline getir
    return "\n".join([f"{c[0]}: {c[1]}" for c in reversed(chats)])

def update_persona_in_db(user_id: int, summary: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_profiles SET persona_summary = %s, last_updated = CURRENT_TIMESTAMP WHERE user_id = %s",
        (summary, user_id)
    )
    conn.commit()
    conn.close()

async def profile_update_task(user_id: int):
    """Arka planda çalışan profil güncelleme görevi"""
    try:
        # 1. Son mesajları çek
        history_text = get_recent_chats(user_id, limit=10)
        
        # 2. LLM'den yeni profil özeti iste (client.py'daki fonksiyon)
        new_profile = await generate_user_profile(history_text)
        
        # 3. Veritabanını güncelle
        update_persona_in_db(user_id, new_profile)
        print(f"✅ Kullanıcı {user_id} için profil güncellendi.")
    except Exception as e:
        print(f"❌ Profilleme Hatası: {e}")

@app.post("/signup")
async def signup(user: UserSignup):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Kullanıcı adı veya Email var mı kontrol et
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user.username, user.email))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Kullanıcı adı veya email zaten kayıtlı.")
        
        # 2. Şifreyi hashle
        hashed_pwd = hash_password(user.password)
        
        # 3. Users tablosuna ekle
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (user.username, user.email, hashed_pwd)
        )
        new_user_id = cursor.fetchone()[0]
        
        # 4. User_profiles tablosuna başlangıç kaydı ekle (ÖNEMLİ)
        cursor.execute(
            "INSERT INTO user_profiles (user_id) VALUES (%s)",
            (new_user_id,)
        )
        
        conn.commit()
        return {"message": "Kayıt başarılı! Giriş yapabilirsiniz."}

    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.post("/login")
async def login(user: UserLogin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kullanıcıyı bul
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (user.username,))
        record = cursor.fetchone()
        
        if record and verify_password(user.password, record[1]):
            # Giriş başarılı - Şimdilik ID dönüyoruz, React Native'de buraya JWT gelecek
            return {
                "status": "success",
                "user_id": record[0],
                "username": user.username,
                "message": f"Hoş geldin {user.username}!"
            }
        
        raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre.")

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()



@app.get("/sessions/{user_id}")
async def get_sessions(user_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT session_id, 
                   MIN(created_at) as created,
                   (SELECT content FROM chat_history ch2 WHERE ch2.session_id = ch1.session_id AND role='user' ORDER BY created_at ASC LIMIT 1) as title
            FROM chat_history ch1
            WHERE user_id = %s
            GROUP BY session_id
            ORDER BY created DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        sessions = [{"session_id": r[0], "title": r[2] if r[2] else "Yeni Sohbet"} for r in rows]
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.get("/chat/{user_id}/{session_id}")
async def get_chat_history(user_id: int, session_id: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = %s AND session_id = %s ORDER BY created_at ASC",
            (user_id, session_id)
        )
        rows = cursor.fetchall()
        history = [{"role": r[0], "content": r[1]} for r in rows]
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.delete("/chat/{user_id}/{session_id}")
async def delete_session(user_id: int, session_id: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id = %s AND session_id = %s", (user_id, session_id))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    if not ctx.session:
        raise HTTPException(status_code=503, detail="MCP Session hazır değil.")
    
    # 1. Önce kullanıcının geçmiş personasını veritabanından çekiyoruz
    user_persona = get_user_persona(request.user_id)
    
    # 2. Mesajı veritabanına kaydet (User)
    save_chat_to_db(request.user_id, "user", request.prompt, request.session_id)
    
    # 3. chat_with_session fonksiyonuna persona bilgisini gönderiyoruz
    # Artık model "Kullanıcı bilim kurgu sever" gibi bilgilere sahip olacak
    answer = await chat_with_session(
        ctx.session, 
        ctx.tools, 
        request.prompt, 
        persona=user_persona
    )
    
    # 4. Asistan yanıtını kaydet
    save_chat_to_db(request.user_id, "assistant", answer, request.session_id)

    # 5. Mesaj sayısını kontrol et ve arka plan görevini yönet
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = %s", (request.user_id,))
    msg_count = cursor.fetchone()[0]
    conn.close()

    if msg_count > 0 and msg_count % 5 == 0:
        background_tasks.add_task(profile_update_task, request.user_id)

    return {"answer": answer}
