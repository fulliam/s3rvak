# models.py

from pydantic import BaseModel
from typing import List, Dict

class Position(BaseModel):
    x: float
    y: float
    z: float

class Health(BaseModel):
    max: int
    current: int
    recovery: float

class Mana(BaseModel):
    max: int
    current: int
    recovery: float

class Stamina(BaseModel):
    max: int
    current: int
    recovery: float

class Crit(BaseModel):
    chance: float
    factor: float

class Attack(BaseModel):
    damage: int
    type: str
    range: int
    level: int

class Money(BaseModel):
    coins: Dict[str, int]
    gems: Dict[str, int]

class Params(BaseModel):
    strength: int
    agility: int
    intelligence: int
    stamina: int
    luck: int

class Skill(BaseModel):
    damage: int
    type: str
    range: int
    level: int

class Skills(BaseModel):
    fireshtorm: Skill
    lighting: Skill
    poisonshtorm: Skill

class CharacterInfo(BaseModel):
    category: str
    character: str
    location: str
    level: int
    experience: int
    levelUpExperience: int

class CharacterState(BaseModel):
    position: Position
    action: str
    health: Health
    mana: Mana
    stamina: Stamina
    armor: int

class CharacterStats(BaseModel):
    speed: Dict[str, int]
    params: Params
    skills: Skills
    skillPoints: int
    statPoints: int
    damage: Dict[str, int]
    attacks: Dict[str, Attack]
    attackSpeed: int
    crit: Crit

class CharacterInventory(BaseModel):
    money: Money
    inventory: List

class Player(BaseModel):
    info: CharacterInfo
    state: CharacterState
    stats: CharacterStats
    inventory: CharacterInventory

class User(BaseModel):
    userId: str
    character: Player

class Message(BaseModel):
    userId: str
    content: str
