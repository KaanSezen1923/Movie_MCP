# client.py (Güncellenmiş hali)
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

async def chat_with_session(session, ollama_tools, prompt):
    """Açık olan session üzerinden tek bir sohbet dönüşü yapar"""
    model_name = 'gemma4:31b-cloud' # Veya llama3.1

    system_instructions = """
    Sen profesyonel bir film danışmanısın. MCP araçlarından gelen verileri işlerken şu kurallara uy:
    1. Yanıtlarını her zaman Türkçe ver.
    2. Eğer birden fazla film listeliyorsan, bunları mutlaka numaralandırılmış bir liste şeklinde sun.
    3. Her film için 'Neden İzlemelisin?' şeklinde bir cümlelik kişisel bir yorum ekle.
    4. Poster linklerini ve fragman linklerini her zaman en sonda 'Medya' başlığı altında göster.
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