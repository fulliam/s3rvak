# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from typing import List
# from app.core.user_manager import user_manager
# from app.models.user import User
# from app.core.security import decode_token

# router = APIRouter()

# # Модель для создания персонажа
# class CharacterCreate(BaseModel):
#     name: str
#     character_type: str
#     stats: dict
#     skills: dict

# # Список доступных типов персонажей (может быть загружен из файла)
# character_types = ['archer', 'swordsman', 'wizard', 'skeleton']

# # GET роут для получения доступных персонажей
# @router.get("/aviable_characters", response_model=List[str])
# async def get_available_characters():
#     return character_types

# # POST роут для создания персонажа с распределёнными характеристиками
# @router.post("/create_character")
# async def create_character(character: CharacterCreate, token: str = Depends(decode_token)):
#     username = token.get("username")
#     user = user_manager.get_user(username)
    
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if character.character_type not in character_types:
#         raise HTTPException(status_code=400, detail="Invalid character type")
    
#     # Создаем нового персонажа
#     new_character = {
#         "name": character.name,
#         "type": character.character_type,
#         "stats": character.stats,
#         "skills": character.skills,
#     }
    
#     user.character = new_character
#     user_manager.add_user(user)
    
#     return {"message": "Character created successfully", "character": new_character}
