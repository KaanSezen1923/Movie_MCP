
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from client import get_ollama_tools, chat_with_session
from dotenv import load_dotenv

load_dotenv()

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env={"AUTH_KEY": os.getenv("AUTH_KEY")}
)

async def main():
    print("🚀 Sunucu başlatılıyor ve oturum açılıyor...")
    
    # 1. BAĞLANTIYI DÖNGÜNÜN DIŞINDA BİR KEZ AÇIYORUZ
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # MCP Initialize
            await session.initialize()
            
            # Tool'ları bir kez çekiyoruz (sürekli değişmiyorsa)
            ollama_tools = await get_ollama_tools(session)
            
            print("✅ Bağlantı hazır! Sorularınızı sorabilirsiniz.")

            while True:
                user_input = input("\nSoru (Çıkmak için 'exit'): ")
                if user_input.lower() == 'exit':
                    break
                
                # 2. HER SEFERİNDE AYNI SESSION'I KULLANIYORUZ
                try:
                    answer = await chat_with_session(session, ollama_tools, user_input)
                    print(f"\n🎬 **Cevap:**\n{answer}")
                except Exception as e:
                    print(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    asyncio.run(main())