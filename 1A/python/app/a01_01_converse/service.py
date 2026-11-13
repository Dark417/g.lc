"""Use cases on top of the showcase: multi-turn chat through the ConversationStore port, demo tools.

- ChatService owns the history rules (window, role order); infra only calls Bedrock.
- DEMO_TOOLS are local functions with JSON-schema specs; handlers validate their own input.
"""

from typing import Any

from app.a01_01_converse.domain import ConversationStore, ConverseResult, ToolDefinition, trim_history
from app.a01_01_converse.infra import ConverseShowcase, user_text

CHAT_SYSTEM = "You are a helpful assistant for backend engineers. Keep answers under 150 words."


class ChatService:
    def __init__(self, showcase: ConverseShowcase, store: ConversationStore) -> None:
        self.showcase = showcase
        self.store = store

    def send(self, conversation_id: str, text: str) -> ConverseResult:
        """Shows: multi-turn over a stateless API: load -> window -> call -> persist both turns.
        Catch: persist the user turn only together with the assistant turn, so a failed call
        never leaves two user messages in a row (ValidationException on the next turn).
        """
        history = self.store.load(conversation_id)
        new_user = user_text(text)
        window = trim_history([*history, new_user], self.showcase.settings.history_max_messages)
        result = self.showcase.converse_messages(window, CHAT_SYSTEM)
        self.store.append(conversation_id, [new_user, result.message])
        return result


# ---------------------------------------------------------------- demo tools (local business code)


def _get_weather(args: dict[str, Any]) -> dict[str, Any]:
    city = str(args["city"]).strip()
    if not city:
        raise ValueError("city must not be empty")
    unit = args.get("unit", "celsius")
    if unit not in ("celsius", "fahrenheit"):
        raise ValueError("unit must be celsius or fahrenheit")
    temp_c = 18 + (sum(map(ord, city.lower())) % 10)  # fake, deterministic
    return {"city": city, "temperature": temp_c if unit == "celsius" else round(temp_c * 9 / 5 + 32), "unit": unit}


def _add_numbers(args: dict[str, Any]) -> dict[str, Any]:
    values = args["values"]
    if not isinstance(values, list) or not all(isinstance(v, (int, float)) for v in values):
        raise TypeError("values must be a list of numbers")
    return {"sum": sum(values)}


DEMO_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="get_weather",
        description="Current temperature for a city. Use only when the user asks about weather.",
        input_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Seattle"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
        },
        handler=_get_weather,
    ),
    ToolDefinition(
        name="add_numbers",
        description="Exact sum of a list of numbers. Use instead of mental arithmetic.",
        input_schema={
            "type": "object",
            "properties": {"values": {"type": "array", "items": {"type": "number"}}},
            "required": ["values"],
        },
        handler=_add_numbers,
    ),
]
