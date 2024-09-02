from fastapi import APIRouter, HTTPException
from app.core.security import get_hashed_password, verify_password, create_token
from app.models.user import User
from app.models.player import Player
from app.models.auth import RegisterRequest, LoginRequest
from app.characters import create_default_player
from app.core.connection_manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()

@router.post("/register")
async def register(request: RegisterRequest):
    username = request.username
    password = request.password
    if username in manager.registered_users:
        return {"message": "Username already exists"}
    hashed_password = get_hashed_password(password)
    default_character = create_default_player()
    user = User(userId=username, username=username, password=hashed_password, character=default_character)
    manager.registered_users[username] = user
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(request: LoginRequest):
    username = request.username
    password = request.password
    user = manager.registered_users.get(username)
    if not user or not verify_password(password, user.password):
        return {"message": "Invalid credentials"}
    token = create_token(username)
    return {"token": token}
