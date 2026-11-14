# 05 · Memory and conversations

Two different things, often confused:

| | Conversation history | Long-term memory |
|---|---|---|
| What | Every message of every session, verbatim | Facts recalled across sessions ("Alice works on the EU launch of Product X") |
| ADK concept | `SessionService` | `MemoryService` |
| Scope | One session | All of one user's sessions |
| Used for | "Show my previous chats", continuing a chat | Better answers without the user repeating context |
| Our impl | `DatabaseSessionService` (SQLite / Postgres) | `SqlMemoryService` (ours) or `VertexAiMemoryBankService` |

## Conversations

- `app_name = "compliance_agent"` everywhere, which is also the ADK agent directory name. So the ADK dev UI and the portal read and write the **same** sessions.
- `user_id` = authenticated email. Users can only list and read sessions under their own `user_id`.
- Title: on the first message, ChatService writes `state["title"]` (first 60 chars) via `state_delta`. Sessions created in the dev UI fall back to "Untitled conversation".
- API:
  - `GET /api/v1/conversations` → `[{id, title, updated_at}]`, newest first
  - `GET /api/v1/conversations/{id}` → messages rebuilt from events: user text, assistant text, verdict cards (from `assess_proposal` function responses), attachments (placeholders)
  - `DELETE /api/v1/conversations/{id}`
- Continuing a conversation = sending `session_id` with the next message.

## Long-term memory

- **Write**: `after_agent_callback` calls `callback_context.add_session_to_memory()` after every turn.
  - `SqlMemoryService.add_session_to_memory` stores user and assistant **text** events, keyed by event id, so re-adding a session is idempotent.
  - Function calls and results are skipped. Verdicts live in the `assessments` table.
- **Read**: ADK's `PreloadMemoryTool` runs before each model call, searches memory with the user's message, and injects matches into the system instruction.
- `SqlMemoryService.search_memory`:
  - scoped to `(app_name, user_id)`: never another user's memories
  - embeds the query, cosine over that user's rows (brute force; one user's history is small)
  - returns top 5 above a similarity floor
- **PRODUCTION**: `MEMORY_BACKEND=vertex` → `VertexAiMemoryBankService` (Agent Engine Memory Bank). It extracts and consolidates *facts* with an LLM instead of storing raw turns. Better recall, less noise, costs model calls.

## Retention and privacy

- Conversations and memories are personal data. `DELETE /api/v1/conversations/{id}` also deletes that session's memories.
- **PRODUCTION**: a retention job (e.g. 365 days), and a "forget me" admin endpoint that deletes by `user_id` across sessions, memories, and assessments.
