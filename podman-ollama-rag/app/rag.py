import argparse
import os
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import OllamaEmbeddings, ChatOllama

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_DIR = "/data/chroma"
DOCS_DIR = "/data/docs"
OUTPUT_DIR = "/data/output"
PROMPTS_DIR = "/data/prompts"

ASK_PROMPT = """Answer the question using only the context below.
If the answer is not in the context, say so.

Context:
{context}

Question: {question}
Answer:
"""

SUMMARY_PROMPT = """Summarize the following retrieved context from a document.
Cover: main topic/argument, key points, and any notable specifics (numbers,
names, quotes) worth remembering. Base this only on the context given - do
not add information not present here.

Context:
{context}

Summary:
"""


def get_embeddings():
    return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_HOST)


def get_llm():
    return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_HOST, temperature=0.3)


def cmd_ingest(args):
    pdf_path = os.path.join(DOCS_DIR, args.pdf)
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {pdf_path} ...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=200
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks.")

    print("Embedding and storing in Chroma (this is the slow step on CPU)...")
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=CHROMA_DIR,
        collection_name=args.collection,
    )
    print(f"Done. Collection '{args.collection}' ready for querying.")


def _get_store(collection):
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
        collection_name=collection,
    )


def cmd_ask(args):
    store = _get_store(args.collection)
    docs = store.similarity_search(args.question, k=args.k)
    context = "\n\n---\n\n".join(d.page_content for d in docs)

    llm = get_llm()

    if args.system_file:
        prompt_path = os.path.join(PROMPTS_DIR, args.system_file)
        if not os.path.exists(prompt_path):
            print(f"Prompt file not found: {prompt_path}", file=sys.stderr)
            sys.exit(1)
        with open(prompt_path) as f:
            system_prompt = f.read()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=ASK_PROMPT.format(context=context, question=args.question)),
        ]
    else:
        messages = ASK_PROMPT.format(context=context, question=args.question)

    response = llm.invoke(messages)
    print(response.content)


def cmd_summarize(args):
    store = _get_store(args.collection)
    # Broad query text to pull a diverse sample of chunks rather than a
    # narrow similarity search - a summary needs coverage, not precision.
    docs = store.similarity_search(
        "main topic, key points, conclusion", k=args.k
    )
    context = "\n\n---\n\n".join(d.page_content for d in docs)

    llm = get_llm()
    prompt = SUMMARY_PROMPT.format(context=context)
    response = llm.invoke(prompt)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{args.collection}-summary.md")
    with open(out_path, "w") as f:
        f.write(response.content)

    print(response.content)
    print(f"\n\nSaved to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Local PDF RAG - ask questions and summarize documents")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Load a PDF into the vector store")
    p_ingest.add_argument("pdf", help="Filename of the PDF inside /data/docs")
    p_ingest.add_argument("--collection", default="default", help="Collection name")
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="Ask a question against an ingested document")
    p_ask.add_argument("question")
    p_ask.add_argument("--collection", default="default")
    p_ask.add_argument("--k", type=int, default=6)
    p_ask.add_argument("--system-file", dest="system_file", default=None,
                       help="Filename of a system prompt inside /data/prompts")
    p_ask.set_defaults(func=cmd_ask)

    p_summary = sub.add_parser("summarize", help="Generate a document summary")
    p_summary.add_argument("--collection", default="default")
    p_summary.add_argument("--k", type=int, default=12)
    p_summary.set_defaults(func=cmd_summarize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
