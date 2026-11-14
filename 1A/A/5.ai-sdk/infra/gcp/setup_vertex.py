"""Create the Vertex AI resources this project uses on the vertex branch.

  cd backend && uv run python ../infra/gcp/setup_vertex.py --project my-proj --bucket my-bucket

1. An Agent Engine instance with no code: it hosts Sessions + Memory Bank for
   VertexAiSessionService, VertexAiMemoryBankService, and our VertexMemoryBank tools.
2. A RAG Engine corpus filled with backend/data/corpus/*.md (uploaded to GCS first).
Prints AGENT_ENGINE_ID and VERTEX_RAG_CORPUS for backend/.env.
"""

import argparse
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[2] / "backend" / "data" / "corpus"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--bucket", required=True, help="GCS bucket (without gs://) for the corpus")
    parser.add_argument("--skip-engine", action="store_true")
    parser.add_argument("--skip-rag", action="store_true")
    args = parser.parse_args()

    import vertexai

    if not args.skip_engine:
        client = vertexai.Client(project=args.project, location=args.location)
        engine = client.agent_engines.create()  # no agent code: Sessions + Memory Bank only
        print(f"AGENT_ENGINE_ID={engine.api_resource.name.split('/')[-1]}")

    if not args.skip_rag:
        from google.cloud import storage
        from vertexai import rag

        bucket = storage.Client(project=args.project).bucket(args.bucket)
        for path in sorted(CORPUS.glob("*.md")):
            bucket.blob(f"corpus/{path.name}").upload_from_filename(path)
        vertexai.init(project=args.project, location=args.location)
        corpus = rag.create_corpus(display_name="ai-sdk-corpus")
        rag.import_files(corpus.name, paths=[f"gs://{args.bucket}/corpus/"])
        print(f"VERTEX_RAG_CORPUS={corpus.name}")


if __name__ == "__main__":
    main()
