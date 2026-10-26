import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.messages import HumanMessage

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_DIR = "/data/chroma"
DEFAULT_COLLECTION = "aap-docs"

ASK_PROMPT = """You are an expert on Red Hat Ansible Automation Platform (AAP).
Answer the question based on the official AAP documentation excerpts below.
Be specific and concise. Include version numbers, component names, and values where present.
If the context does not contain enough information, say what you do know and note the limitation.

Context:
{context}

Question: {question}
Answer:"""

app = FastAPI(title="AAP Docs RAG", description="Local AAP documentation knowledge base")


def _get_store(collection: str) -> Chroma:
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_HOST),
        collection_name=collection,
    )


class AskRequest(BaseModel):
    question: str
    collection: str = DEFAULT_COLLECTION
    k: int = 6


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]
    collection: str


@app.get("/health")
def health():
    return {"status": "ok", "llm": LLM_MODEL, "embed": EMBED_MODEL}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    store = _get_store(req.collection)
    docs = store.similarity_search(req.question, k=req.k)

    if not docs:
        raise HTTPException(status_code=404, detail="No relevant documents found in the collection.")

    context = "\n\n---\n\n".join(
        f"[{d.metadata.get('source_file', 'unknown')}, p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )

    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_HOST, temperature=0.1)
    response = llm.invoke([HumanMessage(content=ASK_PROMPT.format(context=context, question=req.question))])

    sources = [
        {"file": d.metadata.get("source_file", "unknown"), "page": d.metadata.get("page", "?")}
        for d in docs
    ]

    return AskResponse(answer=response.content, sources=sources, collection=req.collection)
