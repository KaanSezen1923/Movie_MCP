# shared.py
from contextlib import AsyncExitStack
from typing import TypedDict, Annotated, List
import operator

class AppContext:
    def __init__(self):
        self.session = None
        self.tools = None
        self.exit_stack = AsyncExitStack()

# Ortak context objesi
ctx = AppContext()

# Ortak tip tanımı
class GraphState(TypedDict):
    prompt: str
    persona: str
    intent: str
    messages: Annotated[List[dict], operator.add]
    final_output: str
    tools: List[dict]