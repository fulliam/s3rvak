from typing import Dict, List
from app.models.user import User

class UserManager:
    def __init__(self):
        self.registered_users: Dict[str, User] = {}

    def add_user(self, user: User):
        self.registered_users[user.userId] = user

    def get_user(self, userId: str) -> User:
        return self.registered_users.get(userId)

    def remove_user(self, userId: str):
        if userId in self.registered_users:
            del self.registered_users[userId]
            
    def get_all_users(self) -> List[User]:
        return list(self.registered_users.values())

# Глобальный экземпляр записей о пользователях
user_manager = UserManager()