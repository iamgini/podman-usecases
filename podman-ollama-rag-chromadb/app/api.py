import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.messages import HumanMessage
from mcp.server.fastmcp import FastMCP

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_DIR = "/data/chroma"
DEFAULT_COLLECTION = "aap-docs"

REWRITE_PROMPT = """You are helping search Red Hat Ansible Automation Platform (AAP) documentation.
Rewrite the following question using the exact terminology AAP documentation uses.
Replace cloud-provider-specific terms with their generic equivalents used in AAP docs.
Examples: "Amazon RDS" → "external PostgreSQL", "IAM role" → "SSL certificate or pg_hba.conf",
"Kubernetes ingress" → "OpenShift route", "S3 bucket" → "object storage".
Output only the rewritten question, nothing else.

Question: {question}
Rewritten:"""

ASK_PROMPT = """You are an expert on Red Hat Ansible Automation Platform (AAP).
Answer the question based on the official AAP documentation excerpts below.
Be specific and concise. Include version numbers, component names, and values where present.
If the context does not contain enough information, say what you do know and note the limitation.

Context:
{context}

Question: {question}
Answer:"""

app = FastAPI(title="AAP Docs RAG", description="Local AAP documentation knowledge base")
mcp = FastMCP("AAP Docs RAG")


def _rewrite_question(question: str, llm: ChatOllama) -> str:
    response = llm.invoke([HumanMessage(content=REWRITE_PROMPT.format(question=question))])
    rewritten = response.content.strip()
    return rewritten if rewritten else question


def _query_rag(question: str, collection: str, k: int) -> tuple[str, list[dict]]:
    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_HOST, temperature=0.1)
    search_query = _rewrite_question(question, llm)

    store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_HOST),
        collection_name=collection,
    )
    docs = store.similarity_search(search_query, k=k)
    if not docs:
        return "No relevant documents found in the collection.", []

    context = "\n\n---\n\n".join(
        f"[{d.metadata.get('source_file', 'unknown')}, p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )
    response = llm.invoke([HumanMessage(content=ASK_PROMPT.format(context=context, question=question))])
    sources = [
        {"file": d.metadata.get("source_file", "unknown"), "page": d.metadata.get("page", "?")}
        for d in docs
    ]
    return response.content, sources


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
    answer, sources = _query_rag(req.question, req.collection, req.k)
    if not sources:
        raise HTTPException(status_code=404, detail=answer)
    return AskResponse(answer=answer, sources=sources, collection=req.collection)


@mcp.tool()
def ask_rag(question: str, collection: str = DEFAULT_COLLECTION, k: int = 6) -> str:
    """Query the local documentation knowledge base and return an answer with sources.

    IMPORTANT: Before calling this tool, rephrase the question using the terminology the
    documentation itself would use — not the user's original phrasing. For example:
    - "Amazon RDS" → "external PostgreSQL database"
    - "IAM role" → "SSL certificate authentication" or "pg_hba.conf"
    - "Kubernetes ingress" → "route" or "OpenShift route"
    - "load balancer" → "automation mesh" or "receptor"
    Use generic infrastructure terms, not cloud-provider-specific ones, unless the docs
    explicitly use that vendor's terminology."""
    answer, sources = _query_rag(question, collection, k)
    if sources:
        source_list = ", ".join(f"{s['file']} p.{s['page']}" for s in sources)
        return f"{answer}\n\nSources: {source_list}"
    return answer


app.mount("/mcp", mcp.sse_app())
