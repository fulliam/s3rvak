# app/api/auth.py
from fastapi import APIRouter, HTTPException
from app.core.security import get_hashed_password, verify_password, create_token
from app.models.user import User
from app.models.auth import RegisterRequest, LoginRequest
from app.characters import create_default_player
from app.core.user_manager import user_manager
from app.core.status import HTTPStatus, StatusMessages

router = APIRouter()

@router.post("/register")
async def register(request: RegisterRequest):
    username = request.username
    password = request.password

    if user_manager.get_user(username) is not None:
        return {"status": HTTPStatus.BAD_REQUEST.value, "message": StatusMessages.USERNAME_EXISTS.value}

    hashed_password = get_hashed_password(password)
    default_character = create_default_player()
    user = User(userId=username, username=username, password=hashed_password, character=default_character)

    user_manager.add_user(user)
    return {"status": HTTPStatus.CREATED.value, "message": StatusMessages.USER_REGISTERED_SUCCESSFULLY.value}

@router.post("/login")
async def login(request: LoginRequest):
    username = request.username
    password = request.password

    user = user_manager.get_user(username)
    
    if user is None or not verify_password(password, user.password):
        return {"status": HTTPStatus.UNAUTHORIZED.value, "message": StatusMessages.INVALID_CREDENTIALS.value}

    token = create_token(username)
    return {"status": HTTPStatus.OK.value, "token": token, "message": StatusMessages.LOGIN_SUCCESSFUL.value}
