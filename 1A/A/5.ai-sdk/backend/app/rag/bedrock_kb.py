"""Bedrock Knowledge Bases retriever (AWS-managed RAG).

Index: the corpus uploaded to S3 and synced into a Knowledge Base (infra/aws/README.md).
API: bedrock-agent-runtime `Retrieve` -> chunks with S3 location and relevance score.
Native framework equivalents: LangGraph `AmazonKnowledgeBasesRetriever`, Strands
`strands_tools.retrieve`. This class is the framework-neutral path behind `search_docs`.
"""

import asyncio

import boto3

from app.rag.base import Passage


class BedrockKbRetriever:
    name = "bedrock_kb"

    def __init__(self, kb_id: str, region: str, client=None):
        self.kb_id = kb_id
        self._client = client or boto3.client("bedrock-agent-runtime", region_name=region)

    async def search(self, query: str, k: int = 4) -> list[Passage]:
        resp = await asyncio.to_thread(
            self._client.retrieve,
            knowledgeBaseId=self.kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": k}},
        )
        out = []
        for r in resp.get("retrievalResults", []):
            loc = r.get("location", {})
            uri = loc.get("s3Location", {}).get("uri") or loc.get("type", "kb")
            out.append(
                Passage(
                    source=uri.rsplit("/", 1)[-1],
                    text=r["content"]["text"],
                    score=float(r.get("score", 0.0)),
                )
            )
        return out
