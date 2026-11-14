from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, description="Omit to start a new conversation")
    user_id: str = "anonymous"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
