from pydantic import BaseModel

class Message(BaseModel):
    userId: str
    content: str