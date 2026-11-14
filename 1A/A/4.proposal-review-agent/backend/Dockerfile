# One image, two entrypoints:
#   service (default):  uvicorn app.main:app          -> Cloud Run service `backend`
#   bulk ingest job:    python -m app.cli ingest gs:// -> Cloud Run job `ingest`

# --- build: resolve deps with uv into a self-contained venv ---
FROM python:3.11-slim AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
RUN uv sync --frozen --no-dev

# --- runtime: non-root ---
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=build --chown=appuser:appuser /app /app
# sample rules + documents for `python -m app.cli seed`; generated data goes to a volume locally
COPY --chown=appuser:appuser data/samples ./data/samples
RUN mkdir -p data/generated && chown appuser:appuser data/generated
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PORT=8000
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os,urllib.request;urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/healthz')"
# Cloud Run sets $PORT.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
