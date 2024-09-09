import bcrypt
import jwt

def get_hashed_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed_password: str) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def create_token(username: str) -> str:
    return jwt.encode({"username": username}, "secret", algorithm="HS256")

def decode_token(token: str) -> dict:
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
    return payload
