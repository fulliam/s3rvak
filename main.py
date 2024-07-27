from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
from pydantic import BaseModel
import json

app = FastAPI()

class User(BaseModel):
    user_id: str
    character: str = "wizard"
    action: str = "idle"

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, User] = {}

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections[user.user_id] = websocket
        self.users[user.user_id] = user
        await self.broadcast_users()

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]
        del self.users[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def broadcast_users(self):
        user_list = [user.dict() for user in self.users.values()]
        await self.broadcast(json.dumps({"type": "users", "data": user_list}))

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    user = User(user_id=user_id)
    await manager.connect(websocket, user)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data["type"] == "action":
                user.character = message_data.get("character", user.character)
                user.action = message_data.get("action", user.action)
                manager.users[user_id] = user
                await manager.broadcast_users()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast_users()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app', port=3000, host='0.0.0.0',
        reload=True)
