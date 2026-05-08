import os
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI, HTTPException,BackgroundTasks
from httpx import request
from pydantic import BaseModel,EmailStr, field_validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from shared import ctx
from client import get_ollama_tools, generate_user_profile, app as graph_app
import psycopg2
import bcrypt

load_dotenv()



@asynccontextmanager
async def lifespan(app: FastAPI):
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"], # Kendi MCP server dosyanızın adı
        env={"AUTH_KEY": os.getenv("AUTH_KEY")}
    )

    print("🚀 MCP Sunucusu ve Session başlatılıyor...")
    try:
        # shared içindeki ctx nesnesini dolduruyoruz
        read, write = await ctx.exit_stack.enter_async_context(stdio_client(server_params))
        ctx.session = await ctx.exit_stack.enter_async_context(ClientSession(read, write))
        
        await ctx.session.initialize()
        
        # Tool'ları çekip shared ctx içine kaydediyoruz
        ctx.tools = await get_ollama_tools(ctx.session)
        print(f"✅ {len(ctx.tools)} adet tool başarıyla yüklendi.")
        
        yield
    finally:
        print("🛑 Sunucu kapatılıyor, kaynaklar temizleniyor...")
        await ctx.exit_stack.aclose()



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
    # Son mesajları al
    cursor.execute(
        "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit)
    )
    chats = cursor.fetchall()
    conn.close()
    
    # HATALI KISIM BURASIYDI: "\n".join(...) yerine liste döndürüyoruz
    return [{"role": c[0], "content": c[1]} for c in reversed(chats)]

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
    try:
        # Liste olarak alıyoruz
        history_list = get_recent_chats(user_id, limit=10)
        
        # LLM'e göndermeden önce metne çeviriyoruz
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history_list])
        
        new_profile = await generate_user_profile(history_text)
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
    
    user_persona = get_user_persona(request.user_id)
    chat_history = get_recent_chats(request.user_id, limit=10) 
    
    initial_state = {
        "prompt": request.prompt,
        "persona": user_persona or "Film sever bir kullanıcı.",
        "messages": chat_history + [{"role": "user", "content": request.prompt}],
        "tools": ctx.tools, # client.py'daki düğüm bunu kullanacak
        "intent": "",
        "final_output": ""
    }
    
    try:
        # graph_app (client.py'daki app) çağrılıyor
        result = await graph_app.ainvoke(initial_state) 
        answer = result.get("final_output", "Üzgünüm, şu an öneri yapamıyorum.")
    except Exception as e:
        print(f"Grafik Hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    save_chat_to_db(request.user_id, "user", request.prompt, request.session_id)
    save_chat_to_db(request.user_id, "assistant", answer, request.session_id)

    # 6. Persona Güncelleme Kontrolü (Arka plan görevi)
    msg_count = get_user_message_count(request.user_id)
    if msg_count > 0 and msg_count % 5 == 0:
        background_tasks.add_task(profile_update_task, request.user_id)

    return {"answer": answer}

def get_user_message_count(user_id: int):
    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = %s", (user_id,))

    msg_count = cursor.fetchone()[0]

    conn.close()
    return msg_count