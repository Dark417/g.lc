# 01bedrock.01converse Conversation State

> Converse is stateless, so the caller stores, trims, and resends history every turn.

## Index

- [1. Stateless By Design](#1-stateless-by-design)
- [2. The Store Port](#2-the-store-port)
- [3. Trimming History](#3-trimming-history)
- [4. The Multi-Turn Use Case](#4-the-multi-turn-use-case)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. Stateless By Design

The service keeps nothing between calls.

- You resend the whole history every turn

  ⇒ cost and latency grow with conversation length

- Per-turn cost otherwise grows linearly with history
  - Cache the stable prefix ([04 prompt caching](01bedrock.01converse.04request-response.md#3-prompt-caching))
  - Summarize old turns once history exceeds a budget

```python
# app/infra/_01bedrock_01converse.py
def converse_messages(self, messages: list[Message], system: str, model_id: str | None = None) -> ConverseResult:
    resp = self.runtime.converse(
        modelId=model_id or self.settings.text_model(),
        system=[{"text": system}],
        messages=messages,  # the full (trimmed) history every turn
        inferenceConfig=self.inference_config(),
    )
    return parse_converse_response(resp)
```

## 2. The Store Port

History lives behind a port so the adapter can change.

- Store history behind a port (`ConversationStore`)
- Production adapter: DynamoDB
  - Partition Key (PK)=`CONV#<id>`, Sort Key (SK)=`MSG#<zero-padded seq>`
  - Time to Live (TTL) on `expiresAt`
  - One item per message
  - 400 Kilobyte (KB) item cap ⇒ large documents go to Simple Storage Service (S3), store a pointer
- Dev adapter: in-memory dict

```python
# app/domain/_01bedrock_01converse.py
class ConversationStore(Protocol):
    """History per conversation. Converse is stateless: the caller resends history every turn."""

    def load(self, conversation_id: str) -> list[Message]: ...
    def append(self, conversation_id: str, messages: list[Message]) -> None: ...
    def clear(self, conversation_id: str) -> None: ...
```

```python
# app/infra/_01bedrock_01converse.py
class InMemoryConversationStore(ConversationStore):
    """Dev/tests only. Production: DynamoDB so any instance can serve the next turn."""

    def __init__(self) -> None:
        self._data: dict[str, list[Message]] = {}

    def load(self, conversation_id: str) -> list[Message]:
        return list(self._data.get(conversation_id, []))

    def append(self, conversation_id: str, messages: list[Message]) -> None:
        self._data.setdefault(conversation_id, []).extend(messages)
```

- Catch: the in-memory store is lost on restart.
- Catch: it is not shared across replicas.

## 3. Trimming History

The window must keep Converse's role rules valid.

- Trim by message count or token budget
- Keep the first `user` message valid
  - Converse requires the first message to be `user`
  - Roles must alternate
- A `toolResult` user message must follow its `toolUse` assistant message
  - Never start the window on one
- Prevents: `ValidationException` on role order and context-window errors

```python
# app/domain/_01bedrock_01converse.py
def trim_history(messages: list[Message], max_messages: int) -> list[Message]:
    if len(messages) <= max_messages:
        return messages
    window = messages[-max_messages:]
    # drop leading messages until the window starts on a plain user turn
    while window and (window[0]["role"] != "user" or _has_tool_result(window[0])):
        window = window[1:]
    return window
```

```python
# app/config/_01bedrock_01converse.py
history_max_messages: int = 20  # sliding window for multi-turn (kept even so roles stay paired)
```

- Limit: a window by count ignores tokens.
  - A token budget (`CountTokens`) is the precise version.

## 4. The Multi-Turn Use Case

The service owns history rules; infra only calls Bedrock.

→ load history  
→ window it  
→ call Converse  
→ persist both turns

```python
# app/service/_01bedrock_01converse.py
CHAT_SYSTEM = "You are a helpful assistant for backend engineers. Keep answers under 150 words."

class ChatService:
    def send(self, conversation_id: str, text: str) -> ConverseResult:
        history = self.store.load(conversation_id)
        new_user = user_text(text)
        window = trim_history([*history, new_user], self.showcase.settings.history_max_messages)
        result = self.showcase.converse_messages(window, CHAT_SYSTEM)
        # persist user + assistant together: a failed call never leaves two user turns in a row
        self.store.append(conversation_id, [new_user, result.message])
        return result
```

- Catch: persisting the user turn alone before the call is a bug.
  - A failed call then leaves two user messages in a row.
  - The next turn fails with `ValidationException`.
