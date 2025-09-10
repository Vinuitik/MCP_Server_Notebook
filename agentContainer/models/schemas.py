from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class HealthResponse(BaseModel):
    status: str

class MCPToolResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
