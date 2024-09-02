from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.connection_manager import ConnectionManager
from app.models.user import User
from app.models.player import Position
from app.characters import characters
import json

router = APIRouter()

manager = ConnectionManager()

@router.websocket("/ws/{userId}")
async def websocket_endpoint(websocket: WebSocket, userId: str):
    if userId not in characters:
        await websocket.close(code=1003, reason="Character not found")
        return

    character = characters[userId]
    user = User(
        userId=userId,
        character=character,
        username="default_username",  # Замените на реальное значение или получите из запроса
        password="default_password"   # Замените на реальное значение или получите из запроса
    )
    
    await manager.connect(websocket, user)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data.get("type") == "action":
                user.character.state.action = message_data.get("action", user.character.state.action)
                manager.users[userId] = user
                await manager.broadcast_action(userId)
            elif message_data.get("type") == "move":
                position_data = message_data.get("position", {})
                direction_data = message_data.get("direction")
                user.character.state.position = Position(**position_data)
                user.character.state.direction = direction_data
                manager.users[userId] = user
                await manager.broadcast_move(userId)
            elif message_data.get("type") == "location":
                user.character.info.location = message_data.get("location")
                manager.users[userId] = user
                await manager.broadcast_users()
            elif message_data.get("type") == "change_character":
                user.character.info.character = message_data.get("character")
                manager.users[userId] = user
                await manager.broadcast_change_character(userId)
            elif message_data.get("type") == "message":
                content = message_data.get("content", "")
                message = Message(userId=userId, content=content)
                manager.messages.append(message)
                await manager.broadcast_messages()
    except WebSocketDisconnect:
        manager.disconnect(userId)
        await manager.broadcast_users()
