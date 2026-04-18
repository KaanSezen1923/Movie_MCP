import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_ollama_tools(session):
    """Sunucudaki tool'ları Ollama formatına çevirir"""
    mcp_tools = await session.list_tools()
    return [
        {
            'type': 'function',
            'function': {
                'name': tool.name,
                'description': tool.description,
                'parameters': tool.inputSchema,
            },
        }
        for tool in mcp_tools.tools
    ]

async def chat_with_session(session, ollama_tools, prompt,persona=None):
    """Açık olan session üzerinden tek bir sohbet dönüşü yapar"""
    model_name = 'minimax-m2.7:cloud ' 
    
    user_context = f"\nKULLANICI PROFİLİ: {persona}" if persona else ""# Veya llama3.1

    system_instructions = """
    Sen profesyonel bir film danışmanısın.{user_context} MCP araçlarından gelen verileri işlerken şu kurallara uy:
    1. Yanıtlarını her zaman Türkçe ver.
    2. Eğer birden fazla film listeliyorsan, bunları mutlaka numaralandırılmış bir liste şeklinde sun.
    3. Her film için 'Neden İzlemelisin?' şeklinde bir cümlelik kişisel bir yorum ekle.
    4. Poster linklerini  fragman linklerini ve platform bilgilerini  her zaman en sonda 'Medya' başlığı altında göster.
    5. Eğer sonuç bulunamazsa, kullanıcıya üzgün olduğunu söyleme, bunun yerine alternatif bir tür öner.
    6. Teknik verileri (ID'ler, ham JSON çıktıları) asla kullanıcıya gösterme.
    """

    messages = [
        {'role': 'system', 'content': system_instructions},
        {'role': 'user', 'content': prompt}
    ]
    
    response = ollama.chat(
        model=model_name,
        messages=messages,
        tools=ollama_tools,
    )

    if response.get('message', {}).get('tool_calls'):
        for tool_call in response['message']['tool_calls']:
            function_name = tool_call['function']['name']
            arguments = tool_call['function']['arguments']
            
            print(f"--- Araç Çağrılıyor: {function_name}")
            result = await session.call_tool(function_name, arguments)
            
            final_response = ollama.chat(
                model=model_name,
                messages=[
                    {'role': 'system', 'content': system_instructions},
                    {'role': 'user', 'content': prompt},
                    response['message'],
                    {'role': 'tool', 'content': result.content[0].text},
                ],
            )
            return final_response['message']['content']
    
    return response['message']['content']

# client.py içine ekle
async def generate_user_profile(chat_history_text):
    """Sohbet geçmişinden kullanıcı ilgi alanlarını analiz eder."""
    model_name = 'minimax-m2.7:cloud' # veya kullandığınız model
    
    profiler_instructions = """
    Sen bir kullanıcı deneyimi analistisin. Aşağıdaki sohbet geçmişini analiz ederek kullanıcı hakkında bir "Persona Özeti" oluştur.
    
    Analizinde şunlara odaklan:
    1. Sevdiği film türleri ve temalar.
    2. Sevmediği veya kaçındığı içerikler.
    3. Favori oyuncuları veya yönetmenleri.
    4. Konuşma tarzı (kısa cevaplar mı veriyor, detaycı mı?).
    
    Çıktın kısa, öz ve üçüncü şahıs ağzından olmalı (Örn: "Kullanıcı bilim kurgu ve gerilim türlerinden hoşlanıyor...").
    """

    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': profiler_instructions},
            {'role': 'user', 'content': f"Sohbet Geçmişi:\n{chat_history_text}"}
        ]
    )
    return response['message']['content']
