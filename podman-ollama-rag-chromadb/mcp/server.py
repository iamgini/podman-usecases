import httpx
from mcp.server.fastmcp import FastMCP

API_URL = "http://localhost:8000"

mcp = FastMCP("local-rag")


@mcp.tool()
def ask_rag(question: str, collection: str = "aap-docs", k: int = 6) -> str:
    """Query the local documentation knowledge base (Red Hat AAP docs by default).

    IMPORTANT: Before calling this tool, rephrase the question using the terminology the
    documentation itself would use — not the user's original phrasing. For example:
    - "Amazon RDS" → "external PostgreSQL database"
    - "IAM role" → "SSL certificate authentication" or "pg_hba.conf"
    - "Kubernetes ingress" → "route" or "OpenShift route"
    - "load balancer" → "automation mesh" or "receptor"
    Use generic infrastructure terms, not cloud-provider-specific ones, unless the docs
    explicitly use that vendor's terminology."""
    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{API_URL}/ask", json={"question": question, "collection": collection, "k": k})
        r.raise_for_status()
        data = r.json()
    sources = ", ".join(f"{s['file']} p.{s['page']}" for s in data["sources"])
    return f"{data['answer']}\n\nSources: {sources}"


if __name__ == "__main__":
    mcp.run()
