# One image, three entrypoints:
#   default                          uvicorn app.main:app                 (k8s, Cloud Run, compose)
#   AgentCore Runtime                python -m app.runtimes.agentcore_app (port 8080)
#   MCP server over HTTP             python -m app.mcp.server --http 8765

# --- build: resolve deps with uv into a self-contained venv ---
FROM python:3.11-slim AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
RUN uv sync --frozen --no-dev

# --- runtime ---
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=build --chown=appuser:appuser /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PORT=8000 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
# Chromium for the `browse` tool (local backend). Skip it if you only use AgentCore Browser.
RUN playwright install --with-deps chromium && chmod -R a+rx /ms-playwright
COPY --chown=appuser:appuser data/corpus ./data/corpus
COPY --chown=appuser:appuser evals ./evals
RUN mkdir -p data/generated && chown appuser:appuser data/generated
USER appuser
EXPOSE 8000 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os,urllib.request;urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/healthz')"
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
