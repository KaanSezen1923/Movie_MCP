import json
import re
from shared import ctx, GraphState
import ollama
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator



class GraphState(TypedDict):
    prompt: str
    persona: str
    intent: str
    messages: Annotated[List[dict], operator.add]
    final_output: str
    tools: List[dict] # API'den gelen tool tanımları

async def analyze_intent_node(state: GraphState):
    model_name = 'gpt-oss:120b-cloud'
    intent_instructions = """
    Sen bir Film Botu Yönlendiricisisin. 
    'recommendation': Film önerisi, detay sorma veya duygusal/mod durumları (üzgünüm, canım sıkkın vb.).
    'general': Sadece selamlaşma.
    Cevap: SADECE kategori adı.
    """
    response = ollama.chat(
        model=model_name,
        messages=[{'role': 'system', 'content': intent_instructions}, {'role': 'user', 'content': state['prompt']}]
    )
    intent = response['message']['content'].strip().lower()
    return {"intent": "recommendation" if "recommendation" in intent else "general"}

async def recommendation_node(state: GraphState):
    model_name = 'gpt-oss:120b-cloud'
    
    # Prompt: JSON şemasını daha kesin belirttik
    system_msg = f"""
    Sen profesyonel bir film danışmanısın. Kullanıcı Personası: {state['persona']}
    GÖREV: Film önerisi yaparken MUTLAKA 'search_movies_by_filters' aracını kullan.
    
    CEVAP FORMATI (SADECE JSON):
    {{
      "type": "movie_list",
      "text": "Kullanıcıya yönelik samimi açıklama metni",
      "movies": [
        {{
          "Film": "Adı",
          "Yıl": "2024",
          "IMDb": "8.5",
          "Türler": "Aksiyon",
          "Özet": "Kısa özet",
          "Poster": "URL",
          "Fragman": "URL",
          "Şu Anki Platform(lar)": "Netflix"
        }}
      ]
    }}
    JSON dışında hiçbir açıklama veya markdown ekleme.
    """

    # 1. Adım: Modelden Tool Call veya Yanıt İste
    response = ollama.chat(
        model=model_name,
        messages=[{'role': 'system', 'content': system_msg}] + state['messages'],
        tools=state['tools']
    )

    message = response.get('message', {})

    # 2. Adım: Eğer model bir Tool çağrısı yaptıysa
    if message.get('tool_calls'):
        # Tool call'u mesaj geçmişine ekle (Modelin ne yaptığını bilmesi için)
        current_messages = [{'role': 'system', 'content': system_msg}] + state['messages']
        current_messages.append(message)

        for tool_call in message['tool_calls']:
            # Aracı çalıştır
            result = await ctx.session.call_tool(
                tool_call['function']['name'], 
                tool_call['function']['arguments']
            )
            
            # Araç sonucunu 'tool' rolüyle ekle
            current_messages.append({
                'role': 'tool',
                'content': result.content[0].text,
                'name': tool_call['function']['name']
            })

        # 3. Adım: Araç sonuçlarıyla birlikte nihai cevabı üret
        final_response = ollama.chat(
            model=model_name,
            messages=current_messages
        )
        raw_content = final_response['message']['content']
    else:
        # Tool çağırmadıysa (veya doğrudan cevap verdiyse)
        raw_content = message.get('content', '')

    # --- JSON Temizleme ve Parsing ---
    # Model bazen metin + JSON verebilir, sadece JSON kısmını ayıklıyoruz
    try:
        # Markdown bloklarını temizle
        clean_json_str = re.sub(r'```json\s?|```', '', raw_content).strip()
        
        # Eğer hala JSON dışında metin varsa, ilk '{' ve son '}' arasını al
        match = re.search(r'(\{.*\})', clean_json_str, re.DOTALL)
        if match:
            clean_json_str = match.group(1)
            
        parsed_data = json.loads(clean_json_str)
        return {"final_output": json.dumps(parsed_data)}
        
    except (json.JSONDecodeError, AttributeError):
        # Fallback: Model JSON formatını bozarsa frontend'in çökmemesi için
        fallback = {
            "type": "movie_list",
            "text": raw_content if raw_content else "Üzgünüm, uygun bir film bulamadım.",
            "movies": []
        }
        return {"final_output": json.dumps(fallback)}

   

async def general_chat_node(state: GraphState):
    response = ollama.chat(model='gpt-oss:120b-cloud', messages=state['messages'])
    return {"final_output": response['message']['content']}

# --- Grafik Kurulumu ---
def route_by_intent(state: GraphState):
    return "recommendation_engine" if state["intent"] == "recommendation" else "general_chatter"

workflow = StateGraph(GraphState)
workflow.add_node("intent_analyzer", analyze_intent_node)
workflow.add_node("recommendation_engine", recommendation_node)
workflow.add_node("general_chatter", general_chat_node)

workflow.set_entry_point("intent_analyzer")
workflow.add_conditional_edges("intent_analyzer", route_by_intent)
workflow.add_edge("recommendation_engine", END)
workflow.add_edge("general_chatter", END)

app = workflow.compile()

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

async def generate_user_profile(chat_history_text):
    """Sohbet geçmişinden kullanıcı ilgi alanlarını analiz eder."""
    model_name = 'gpt-oss:120b-cloud' # veya kullandığınız model
    
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