from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List
import json
from models import User, Message, Player, Position
from characters import characters

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, User] = {}
        self.messages: List[Message] = []

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections[user.userId] = websocket
        self.users[user.userId] = user
        await self.send_personal_message(json.dumps(user.character.dict()), websocket)
        await self.broadcast_users()

    def disconnect(self, userId: str):
        if userId in self.active_connections:
            del self.active_connections[userId]
        if userId in self.users:
            del self.users[userId]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def broadcast_users(self):
        user_list = [user.dict() for user in self.users.values()]
        await self.broadcast(json.dumps({"type": "users", "data": user_list}))

    async def broadcast_move(self, user_id: str):
        move_list = {
            "userId": user_id,
            "coords": self.users[user_id].character.state.position.dict(),
            "direction": self.users[user_id].character.state.direction
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

@app.websocket("/ws/{userId}")
async def websocket_endpoint(websocket: WebSocket, userId: str):
    if userId not in characters:
        await websocket.close(code=1003, reason="Character not found")
        return

    character = characters[userId]
    user = User(userId=userId, character=character)
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

@app.post("/update_character/{userId}")
async def update_character(userId: str, character_update: Player):
    if userId not in manager.users:
        raise HTTPException(status_code=404, detail="User not found")
    manager.users[userId].character = character_update
    await manager.broadcast_users()
    return {"message": "Character updated successfully"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=3000, host='0.0.0.0', reload=True)
