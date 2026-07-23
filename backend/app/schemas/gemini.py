from pydantic import BaseModel
from typing import List, Literal


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    text: str


class GeminiChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class GeminiChatResponse(BaseModel):
    response: str
