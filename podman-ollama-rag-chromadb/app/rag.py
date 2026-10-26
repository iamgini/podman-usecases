import argparse
import os
import re
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
DESIGNS_DIR = "/data/designs"
OUTPUT_DIR = "/data/output"
PROMPTS_DIR = "/data/prompts"

DEFAULT_COLLECTION = "aap-docs"

ASK_PROMPT = """Answer the question using only the context below.
If the answer is not in the context, say so.

Context:
{context}

Question: {question}
Answer:
"""

VALIDATE_PROMPT = """DESIGN DOCUMENT:
{design_doc}

OFFICIAL AAP DOCUMENTATION EXCERPTS:
{context}

Review the design document against the documentation excerpts and produce a structured validation report.
"""


def get_embeddings():
    return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_HOST)


def get_llm():
    return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_HOST, temperature=0.1)


def _get_store(collection):
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
        collection_name=collection,
    )


def _load_prompt(filename):
    path = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def _resolve_includes(text, base_dir, depth=0):
    """Recursively resolve include:: directives in adoc content."""
    if depth > 5:
        return text

    def replace_include(m):
        include_path = m.group(1)
        full_path = os.path.join(base_dir, include_path)
        if os.path.exists(full_path):
            try:
                with open(full_path) as f:
                    included = f.read()
                sub_dir = os.path.dirname(full_path)
                return _resolve_includes(included, sub_dir, depth + 1)
            except Exception:
                return ""
        return ""

    return re.sub(r'include::([^\[]+)\[.*?\]', replace_include, text)


def _strip_adoc(text):
    """Remove asciidoc markup to get plain text suitable for embedding queries."""
    text = re.sub(r'^\[.*?\]$', '', text, flags=re.MULTILINE)
    text = re.sub(r'image::.*?\[.*?\]', '', text)
    text = re.sub(r'\{[^}]+\}', '', text)
    text = re.sub(r'^[=]+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'^\|.*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _split_adoc_sections(text):
    """Split adoc content into sections by == headings. Returns list of (title, body) tuples."""
    sections = []
    current_title = "preamble"
    current_lines = []

    for line in text.splitlines():
        m = re.match(r'^(={1,4})\s+(.+)', line)
        if m:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines)))
            current_title = m.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines)))

    return sections


def cmd_ingest(args):
    """Ingest a single PDF into the vector store."""
    pdf_path = os.path.join(DOCS_DIR, args.pdf)
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {args.pdf} ...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    for page in pages:
        page.metadata["source_file"] = args.pdf

    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks. Embedding...")

    store = _get_store(args.collection)
    store.add_documents(chunks)
    print(f"Done. '{args.pdf}' added to collection '{args.collection}'.")


def cmd_ingest_dir(args):
    """Ingest all PDFs in /data/docs into the vector store."""
    pdfs = sorted(f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf"))
    if not pdfs:
        print(f"No PDFs found in {DOCS_DIR}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF(s) to ingest into collection '{args.collection}':")
    for p in pdfs:
        print(f"  - {p}")
    print()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    store = _get_store(args.collection)

    for pdf in pdfs:
        pdf_path = os.path.join(DOCS_DIR, pdf)
        print(f"[{pdfs.index(pdf)+1}/{len(pdfs)}] Loading {pdf} ...")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        for page in pages:
            page.metadata["source_file"] = pdf

        chunks = splitter.split_documents(pages)
        print(f"  → {len(chunks)} chunks, embedding...")
        store.add_documents(chunks)
        print(f"  ✓ done")

    print(f"\nAll {len(pdfs)} PDF(s) ingested into collection '{args.collection}'.")


def cmd_validate(args):
    """Validate a design doc (.adoc) against the AAP docs RAG."""
    design_path = os.path.join(DESIGNS_DIR, args.design)
    if not os.path.exists(design_path):
        print(f"Design doc not found: {design_path}", file=sys.stderr)
        sys.exit(1)

    with open(design_path) as f:
        raw_content = f.read()

    # Resolve include:: directives so sub-files are inlined
    base_dir = os.path.dirname(design_path)
    resolved_content = _resolve_includes(raw_content, base_dir)
    clean_content = _strip_adoc(resolved_content)
    sections = _split_adoc_sections(clean_content)
    print(f"Content length after include resolution: {len(clean_content)} chars")

    print(f"Design doc: {args.design}")
    print(f"Sections found: {len(sections)}")
    print(f"Querying collection '{args.collection}' for relevant AAP doc chunks...")

    store = _get_store(args.collection)

    # Query each section for relevant chunks, deduplicate
    seen = set()
    all_chunks = []
    for title, body in sections:
        if not body.strip():
            continue
        query = f"{title}: {body[:400]}"
        docs = store.similarity_search(query, k=args.k)
        for doc in docs:
            key = doc.page_content[:100]
            if key not in seen:
                seen.add(key)
                all_chunks.append(doc)

    # Cap total context to avoid overwhelming the LLM
    context_chunks = all_chunks[:args.max_chunks]
    context = "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source_file', 'unknown')}, p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in context_chunks
    )

    print(f"Retrieved {len(context_chunks)} unique chunks. Running validation...")

    system_prompt = _load_prompt("validate.txt")
    if not system_prompt:
        print("Warning: validate.txt prompt not found, using default.", file=sys.stderr)
        system_prompt = "You are an AAP Solutions Architect reviewing a design document. Validate it against the provided documentation context."

    # Truncate design doc if very large (keep most important parts)
    design_for_prompt = clean_content[:10000]
    if len(clean_content) > 10000:
        print(f"Note: design doc truncated to 10000 chars for LLM context (original: {len(clean_content)})")

    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=VALIDATE_PROMPT.format(
            design_doc=design_for_prompt,
            context=context,
        )),
    ]

    response = llm.invoke(messages)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    report_name = os.path.basename(args.design).replace(".adoc", "-validation.md")
    out_path = os.path.join(OUTPUT_DIR, report_name)
    with open(out_path, "w") as f:
        f.write(f"# Validation Report\n")
        f.write(f"**Design doc:** `{args.design}`  \n")
        f.write(f"**Collection:** `{args.collection}`  \n")
        f.write(f"**Chunks used:** {len(context_chunks)}  \n\n")
        f.write(response.content)

    print("\n" + "="*60)
    print(response.content)
    print("="*60)
    print(f"\nReport saved to: {out_path}")


def cmd_ask(args):
    """Ask a free-form question against an ingested collection."""
    store = _get_store(args.collection)
    docs = store.similarity_search(args.question, k=args.k)
    context = "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source_file', 'unknown')}, p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )

    llm = get_llm()
    system_file = args.system_file or "rag-prompt.txt"
    system_prompt = _load_prompt(system_file)

    if system_prompt:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=ASK_PROMPT.format(context=context, question=args.question)),
        ]
    else:
        messages = [HumanMessage(content=ASK_PROMPT.format(context=context, question=args.question))]

    response = llm.invoke(messages)
    print(response.content)


def main():
    parser = argparse.ArgumentParser(
        description="AAP Doc RAG — ingest AAP documentation PDFs and validate design documents"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest: single PDF
    p_ingest = sub.add_parser("ingest", help="Ingest a single PDF into the vector store")
    p_ingest.add_argument("pdf", help="Filename of the PDF inside /data/docs")
    p_ingest.add_argument("--collection", default=DEFAULT_COLLECTION)
    p_ingest.set_defaults(func=cmd_ingest)

    # ingest-dir: all PDFs in /data/docs
    p_ingest_dir = sub.add_parser("ingest-dir", help="Ingest all PDFs in /data/docs into the vector store")
    p_ingest_dir.add_argument("--collection", default=DEFAULT_COLLECTION)
    p_ingest_dir.set_defaults(func=cmd_ingest_dir)

    # validate: validate a design doc .adoc file
    p_validate = sub.add_parser("validate", help="Validate a design doc (.adoc) against the AAP docs")
    p_validate.add_argument("design", help="Relative path to .adoc file under /data/designs (e.g. sg-gic-aap-27-on-ocp-prod-uat-design/content/150_architecture.adoc)")
    p_validate.add_argument("--collection", default=DEFAULT_COLLECTION)
    p_validate.add_argument("--k", type=int, default=5, help="Chunks to retrieve per section (default: 5)")
    p_validate.add_argument("--max-chunks", dest="max_chunks", type=int, default=25, help="Max total chunks sent to LLM (default: 25)")
    p_validate.set_defaults(func=cmd_validate)

    # ask: free-form Q&A
    p_ask = sub.add_parser("ask", help="Ask a question against an ingested collection")
    p_ask.add_argument("question")
    p_ask.add_argument("--collection", default=DEFAULT_COLLECTION)
    p_ask.add_argument("--k", type=int, default=6)
    p_ask.add_argument("--system-file", dest="system_file", default=None)
    p_ask.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
