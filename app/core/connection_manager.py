from typing import Dict, List
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
import json
from app.models.user import User
from app.models.message import Message
from app.models.player import Position
from app.core.user_manager import user_manager
from app.core.helpers.attack import calculate_distance, is_target_in_attack_direction
from time import time
import asyncio
from random import random

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

    async def broadcast_attack(self, user_id: str, attack_data: dict):
        attacker = self.users.get(user_id)
        if not attacker:
            return
        
        attack_range = attack_data.get("range", 0)
        attack_damage = attack_data.get("damage", 0)
        attack_position = attacker.character.state.position
        attack_direction = attacker.character.state.direction

        attacked_users = []

        for user in self.users.values():
            if user.userId != user_id:
                distance = calculate_distance(attack_position, user.character.state.position)
                
                if distance <= attack_range and is_target_in_attack_direction(attacker, user.character.state.position):
                    is_critical = random() < attacker.character.stats.crit.chance
                    final_damage = attack_damage
                    if is_critical:
                        final_damage *= attacker.character.stats.crit.factor
                    
                    user.character.state.health.current = max(0, user.character.state.health.current - final_damage)
                    
                    if user.character.state.health.current <= 0:
                        user.character.state.action = 'dead'
                        await self.broadcast_action(user.userId)

                    attacked_users.append({
                        "userId": user.userId,
                        "health": user.character.state.health.current,
                        "action": user.character.state.action
                    })
        
        attack_event = {
            "userId": user_id,
            "attack": attack_data,
            "affectedUsers": attacked_users,
        }
        
        await self.broadcast(json.dumps({"type": "attack", "update": attack_event}))

    async def broadcast_move(self, user_id: str):
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

    def recover_health_for_connected_users(self):
        current_time = time()
        for user_id, user in self.users.items():
            if user.character.state.action == 'dead':
                continue
            
            last_time = user_manager.last_recovery_time.get(user_id, current_time)
            time_since_last_recovery = current_time - last_time
            
            if time_since_last_recovery >= 1:
                recovery_amount = int(user.character.state.health.recovery)
                user.character.state.health.current = min(
                    user.character.state.health.max,
                    user.character.state.health.current + recovery_amount
                )
                user_manager.last_recovery_time[user_id] = current_time
                asyncio.create_task(self.broadcast_health_update(user_id))
    
    async def broadcast_health_update(self, user_id: str):
        user = self.users.get(user_id)
        if user:
            health_data = {
                "userId": user_id,
                "health": {
                    "current": user.character.state.health.current,
                    "max": user.character.state.health.max
                }
            }
            await self.broadcast(json.dumps({"type": "health_recovery", "update": health_data}))

manager = ConnectionManager()