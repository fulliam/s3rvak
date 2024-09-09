from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from app.core.connection_manager import manager
from app.core.user_manager import user_manager
from app.models.user import User
from app.models.player import Position
from app.characters import characters
import json
from app.core.security import decode_token

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
            print(f"Token username {token_username} does not match userId {userId}")
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception as e:
        print(f"Error during token validation: {str(e)}")
        await websocket.close(code=1008, reason="Invalid token")
        return

    player = user_manager.get_user(userId)
    if player is None:
        await websocket.close(code=1003, reason="User not found")
        return

    user = User(
        userId=userId,
        character=player.character,
        username=player.username,
        password=player.password
    )

    await manager.connect(websocket, user)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = message_data.get("type")

            if message_type == "action":
                user.character.state.action = message_data.get("action", user.character.state.action)
                user_manager.add_user(user)
                await manager.broadcast_action(userId)
            elif message_type == "move":
                position_data = message_data.get("position", {})
                direction_data = message_data.get("direction")
                user.character.state.position = Position(**position_data)
                user.character.state.direction = direction_data
                user_manager.add_user(user)
                await manager.broadcast_move(userId)
            elif message_type == "location":
                user.character.info.location = message_data.get("location")
                user_manager.add_user(user)
                await manager.broadcast_users()
            elif message_type == "change_character":
                user.character.info.character = message_data.get("character")
                user_manager.add_user(user)
                await manager.broadcast_change_character(userId)
            elif message_type == "message":
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
