from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routes import router

app = FastAPI(
    title="LinkSage API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <html>
    <head>
        <title>LinkSage API</title>
        <style>
            body { background:#111; color:#eee; font-family:Arial,Helvetica,sans-serif; padding:2rem; }
            a { color:#4ea3ff; }
            .container { max-width:800px; margin:auto; }
            h1 { color:#4ea3ff; }
            table { width:100%; border-collapse:collapse; margin-top:1rem; }
            th, td { border:1px solid #333; padding:0.5rem; text-align:left; }
            th { background:#222; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LinkSage Backend</h1>
            <p>AI‑driven bookmark management service.</p>
            <h2>Available Endpoints</h2>
            <table>
                <tr><th>Method</th><th>Path</th><th>Description</th></tr>
                <tr><td>GET</td><td>/health</td><td>Health check</td></tr>
                <tr><td>GET</td><td>/</td><td>Landing page (this)</td></tr>
                <tr><td>POST</td><td>/api/summarize</td><td>Generate one‑sentence summary</td></tr>
                <tr><td>POST</td><td>/api/tag</td><td>Generate hierarchical tags</td></tr>
                <tr><td>GET</td><td>/api/search?q=...</td><td>Semantic search (stub)</td></tr>
            </table>
            <p>Tech Stack: FastAPI 0.115.0, PostgreSQL, DigitalOcean Serverless Inference, Pydantic 2.9.0.</p>
            <p>Docs: <a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")