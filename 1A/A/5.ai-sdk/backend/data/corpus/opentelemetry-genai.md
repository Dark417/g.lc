# OpenTelemetry for agents

## GenAI semantic conventions

- OpenTelemetry defines semantic conventions for generative AI: spans for model calls (operation chat), agent invocations (invoke_agent), and tool executions (execute_tool).
- Common attributes: gen_ai.system / gen_ai.provider.name, gen_ai.request.model, gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, gen_ai.agent.name, gen_ai.tool.name.
- Prompt and completion content is opt-in because it may contain sensitive data.

## Framework support

- ADK and Strands emit GenAI spans natively to the global tracer provider.
- LangChain/LangGraph and the Anthropic SDK are instrumented by OpenInference instrumentors (Arize), which produce OpenTelemetry spans.
- Claude Code (and so the Claude Agent SDK) exports metrics, log events, and traces via OTLP when CLAUDE_CODE_ENABLE_TELEMETRY=1.

## Backends

- Local: an OpenTelemetry Collector forwarding to Jaeger, or Arize Phoenix for LLM-aware views.
- AWS: the ADOT collector sends traces to AWS X-Ray and CloudWatch (AgentCore Observability).
- GCP: Cloud Trace via the Cloud Trace exporter or the OTLP endpoint telemetry.googleapis.com.
