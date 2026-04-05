from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    speaker: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
