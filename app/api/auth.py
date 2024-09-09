from fastapi import APIRouter, HTTPException
from app.core.security import get_hashed_password, verify_password, create_token
from app.models.user import User
from app.models.player import Player
from app.models.auth import RegisterRequest, LoginRequest
from app.characters import create_default_player
from app.core.user_manager import user_manager

router = APIRouter()

@router.post("/register")
async def register(request: RegisterRequest):
    username = request.username
    password = request.password

    # Проверяем, существует ли уже пользователь с таким именем
    if user_manager.get_user(username) is not None:
        return {"message": "Username already exists"}

    # Если пользователь не найден, регистрируем нового
    hashed_password = get_hashed_password(password)
    default_character = create_default_player()
    user = User(userId=username, username=username, password=hashed_password, character=default_character)

    user_manager.add_user(user)
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(request: LoginRequest):
    username = request.username
    password = request.password

    user = user_manager.get_user(username)
    
    if user is None or not verify_password(password, user.password):
        return {"message": "Invalid credentials"}

    token = create_token(username)
    return {"token": token}
