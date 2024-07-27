from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
from pydantic import BaseModel
import json

app = FastAPI()

class User(BaseModel):
    userId: str
    character: str = "wizard"
    action: str = "idle"

class Message(BaseModel):
    userId: str
    content: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, User] = {}
        self.messages: List[Message] = []

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections[user.userId] = websocket
        self.users[user.userId] = user
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

    async def broadcast_messages(self):
        message_list = [message.dict() for message in self.messages]
        await self.broadcast(json.dumps({"type": "messages", "data": message_list}))

manager = ConnectionManager()

@app.websocket("/ws/{userId}")
async def websocket_endpoint(websocket: WebSocket, userId: str):
    user = User(userId=userId)
    await manager.connect(websocket, user)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data.get("type") == "action":
                user.character = message_data.get("character", user.character)
                user.action = message_data.get("action", user.action)
                manager.users[userId] = user
                await manager.broadcast_users()
            elif message_data.get("type") == "message":
                content = message_data.get("content", "")
                message = Message(userId=userId, content=content)
                manager.messages.append(message)
                await manager.broadcast_messages()
    except WebSocketDisconnect:
        manager.disconnect(userId)
        await manager.broadcast_users()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app', port=3000, host='0.0.0.0',
        reload=True)
