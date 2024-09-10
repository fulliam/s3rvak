from typing import Dict, List
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
import json
from app.models.user import User
from app.models.message import Message
from app.models.player import Position
from app.core.user_manager import user_manager

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, User] = {}
        self.messages: List[Message] = []

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections[user.userId] = websocket
        self.users[user.userId] = user
        user_manager.add_user(user)
        await self.send_personal_message(json.dumps(user.character.dict()), websocket)
        await self.broadcast_users()

    def disconnect(self, userId: str):
        if userId in self.active_connections:
            del self.active_connections[userId]
        if userId in self.users:
            del self.users[userId]
        # user_manager.remove_user(userId)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            if connection.client_state != WebSocketState.DISCONNECTED:
                try:
                    await connection.send_text(message)
                except RuntimeError as e:
                    if "websocket.close" in str(e):
                        continue
                    else:
                        raise

    async def broadcast_users(self):
        user_list = [user.dict() for user in self.users.values()]
        await self.broadcast(json.dumps({"type": "users", "data": user_list}))

    async def broadcast_move(self, user_id: str):
        # Обновление позиции пользователя
        new_position = self.users[user_id].character.state.position
        new_direction = self.users[user_id].character.state.direction
        user_manager.update_user_position(user_id, new_position, new_direction)
        
        move_list = {
            "userId": user_id,
            "coords": new_position.dict(),
            "direction": new_direction
        }
        await self.broadcast(json.dumps({"type": "move", "update": move_list}))

    async def broadcast_action(self, user_id: str):
        action_data = {
            "userId": user_id,
            "action": self.users[user_id].character.state.action
        }
        await self.broadcast(json.dumps({"type": "action", "update": action_data}))

    async def broadcast_change_character(self, user_id: str):
        character_data = {
            "userId": user_id,
            "character": self.users[user_id].character.info.character
        }
        await self.broadcast(json.dumps({"type": "change_character", "update": character_data}))

    async def broadcast_messages(self):
        message_list = [message.dict() for message in self.messages]
        await self.broadcast(json.dumps({"type": "messages", "data": message_list}))

manager = ConnectionManager()