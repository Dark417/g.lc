"""Create the AgentCore Memory resource this project uses on the bedrock branch.

  cd backend && uv run python ../infra/aws/setup_agentcore.py --region us-east-1

Strategies decide what long-term memory AgentCore extracts from conversation events:
  semantic        facts            -> /users/{actorId}/facts   (read by app/memory/agentcore.py,
                                                              LangGraph AgentCoreMemoryStore)
  summary         per-session gist -> /summaries/{actorId}/{sessionId}
  user preference preferences      -> /users/{actorId}/preferences
Prints AGENTCORE_MEMORY_ID for backend/.env.
"""

import argparse

from bedrock_agentcore.memory import MemoryClient

STRATEGIES = [
    {"semanticMemoryStrategy": {"name": "facts", "namespaces": ["/users/{actorId}/facts"]}},
    {
        "summaryMemoryStrategy": {
            "name": "summaries",
            "namespaces": ["/summaries/{actorId}/{sessionId}"],
        }
    },
    {
        "userPreferenceMemoryStrategy": {
            "name": "preferences",
            "namespaces": ["/users/{actorId}/preferences"],
        }
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--name", default="ai_sdk_memory")
    parser.add_argument("--expiry-days", type=int, default=30)
    args = parser.parse_args()

    client = MemoryClient(region_name=args.region)
    memory = client.create_memory_and_wait(
        name=args.name,
        strategies=STRATEGIES,
        description="ai-sdk tutorial: short-term events + extracted long-term memory",
        event_expiry_days=args.expiry_days,
    )
    memory_id = memory.get("id") or memory.get("memoryId")
    print(f"AGENTCORE_MEMORY_ID={memory_id}")


if __name__ == "__main__":
    main()
