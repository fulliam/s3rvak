from math import sqrt, degrees, acos
from app.models.player import Position
from app.models.user import User

def calculate_distance(pos1: Position, pos2: Position) -> float:
    return sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)

def is_target_in_attack_direction(attacker: User, target_position: Position) -> bool:
    attack_position = attacker.character.state.position
    attack_direction = attacker.character.state.direction
    
    attack_direction_vector = get_direction_vector(attack_direction)
    
    target_vector = Position(
        x=target_position.x - attack_position.x,
        y=target_position.y - attack_position.y
    )
    
    angle_between_vectors = calculate_angle_between_vectors(attack_direction_vector, target_vector)
    
    allowed_angle = 45
    
    return angle_between_vectors <= allowed_angle

def get_direction_vector(direction: str) -> Position:
    if direction == 'left':
        return Position(x=-1, y=0)
    elif direction == 'right':
        return Position(x=1, y=0)
    else:
        return Position(x=0, y=0)

def calculate_angle_between_vectors(vector1: Position, vector2: Position) -> float:
    dot_product = vector1.x * vector2.x + vector1.y * vector2.y
    magnitude1 = sqrt(vector1.x ** 2 + vector1.y ** 2)
    magnitude2 = sqrt(vector2.x ** 2 + vector2.y ** 2)
    cos_theta = dot_product / (magnitude1 * magnitude2)
    angle = degrees(acos(cos_theta))
    return angle