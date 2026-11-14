# Amazon Bedrock for agents

## Model access

- The Converse API (bedrock-runtime converse / converse_stream) gives one request shape for every Bedrock model, including tool use. Strands BedrockModel, LangChain ChatBedrockConverse, and LiteLLM's bedrock/converse route use it.
- Cross-region inference profiles (ids prefixed us., eu., apac., global.) route requests across regions for capacity.
- Claude in Amazon Bedrock also serves the Anthropic Messages API shape through the AnthropicBedrockMantle client, with model ids prefixed anthropic. (for example anthropic.claude-opus-5).
- Credentials come from the standard AWS chain: environment, profile, SSO, or an IAM role.

## Knowledge Bases

- Managed RAG: point a Knowledge Base at S3 (or other sources), choose an embedding model and vector store, and sync.
- Retrieve returns chunks with scores and source locations; RetrieveAndGenerate also writes the answer.
- Integrations: LangChain AmazonKnowledgeBasesRetriever, Strands retrieve tool.

## Guardrails

- Configurable policies: content filters, denied topics, word filters, sensitive information (PII block or mask), contextual grounding, and automated reasoning checks.
- Attach a guardrail to a model call (guardrailConfig in Converse; guardrail_id in Strands BedrockModel) or call ApplyGuardrail on any text, independent of the model.

## Sessions

- Bedrock Session Management APIs persist conversation checkpoints; LangGraph's BedrockSessionSaver uses them.
- For agent memory with extraction, see AgentCore Memory.
