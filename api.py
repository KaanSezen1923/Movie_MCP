import os
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from client import get_ollama_tools, chat_with_session

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

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    answer: str
@app.post("/chat")
async def chat(request: ChatRequest):
    if not ctx.session:
        raise HTTPException(status_code=503, detail="MCP Session hazır değil.")
    
    try:
        # ctx nesnesi üzerinden session'a erişiyoruz
        answer = await chat_with_session(ctx.session, ctx.tools, request.prompt)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))