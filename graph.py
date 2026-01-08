from typing import TypedDict
from langgraph.graph import StateGraph, END
from gemini import get_gemini_response

class RepoState(TypedDict):
    repo_url: str
    question: str
    context: str
    answer: str

def llm_node(state: RepoState):
    # We combine the context (files) and the question here
    prompt = f"Repo: {state['repo_url']}\nFiles: {state['context']}\nQuestion: {state['question']}"
    answer = get_gemini_response(prompt)
    return {"answer": answer}

def build_graph():
    workflow = StateGraph(RepoState)
    workflow.add_node("llm", llm_node)
    workflow.set_entry_point("llm")
    workflow.add_edge("llm", END)
    return workflow.compile()

app_graph = build_graph()