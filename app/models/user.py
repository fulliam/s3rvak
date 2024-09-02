from pydantic import BaseModel
from .player import Player

class User(BaseModel):
    userId: str
    username: str
    password: str
    character: Player
