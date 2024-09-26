from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from app.core.connection_manager import manager
from app.core.user_manager import user_manager
from app.models.user import User
from app.models.message import Message
from app.models.player import Position
import json
from app.core.security import decode_token
from app.core.status import HTTPStatus, StatusMessages
from app.characters import create_random_enemy

router = APIRouter()

@router.websocket("/ws/{userId}")
async def websocket_endpoint(
    websocket: WebSocket, 
    userId: str, 
    token: str = Query(...)
):
    try:
        payload = decode_token(token)
        token_username = payload.get("username")
        if token_username != userId:
            await websocket.close(code=HTTPStatus.POLICY_VIOLATION.value)
            return
    except Exception:
        await websocket.close(code=HTTPStatus.POLICY_VIOLATION.value)
        return

    player = user_manager.get_user(userId)
    if player is None:
        await websocket.close(code=HTTPStatus.NO_STATUS.value)
        return

    user = User(
        userId=userId,
        character=player.character,
        username=player.username,
        password=player.password
    )

    await manager.connect(websocket, user)

    enemies = [create_random_enemy() for _ in range(20)]  # Создание 5 случайных врагов
    await websocket.send_text(json.dumps({"type": "initial_enemies", "enemies": [enemy.dict() for enemy in enemies]}))
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = message_data.get("type")

            if message_type == "action":
                user.character.state.action = message_data.get("action", user.character.state.action)
                user_manager.add_user(user)
                await manager.broadcast_action(userId)
                
            if message_type == "attack":
                attack_data = message_data.get("attack", {})

                await manager.broadcast_attack(userId, attack_data)

            if message_type == "move":
                position_data = message_data.get("position", {})
                direction_data = message_data.get("direction")
                
                new_position = Position(**position_data)
                user_manager.update_user_position(userId, new_position, direction_data)

                user.character.state.position = new_position
                user.character.state.direction = direction_data
                await manager.broadcast_move(userId)
                
            if message_type == "location":
                user.character.info.location = message_data.get("location")
                user_manager.add_user(user)
                await manager.broadcast_users()

            if message_type == "change_character":
                user.character.info.character = message_data.get("character")
                user_manager.add_user(user)
                await manager.broadcast_change_character(userId)

            if message_type == "message":
                content = message_data.get("content", "")
                message = Message(userId=userId, content=content)
                manager.messages.append(message)
                await manager.broadcast_messages()

            else:
                await websocket.send_text(json.dumps({"error": "Invalid message type"}))

    except WebSocketDisconnect:
        manager.disconnect(userId)
        await manager.broadcast_users()
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
        manager.disconnect(userId)
        await manager.broadcast_users()
