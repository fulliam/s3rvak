from enum import Enum

class HTTPStatus(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    POLICY_VIOLATION = 1008
    NO_STATUS = 1003
    CUSTOM_CONNECTION_REJECTED = 4000

class StatusMessages(Enum):
    USERNAME_EXISTS = "Username already exists"
    USER_REGISTERED_SUCCESSFULLY = "User registered successfully"
    INVALID_CREDENTIALS = "Invalid credentials"
    LOGIN_SUCCESSFUL = "Login successful"
    INVALID_TOKEN = "Invalid token"
    USER_NOT_FOUND = "User not found"
    CONNECTION_REJECTED = "Connection rejected"
    CONNECTION_CLOSED = "Connection closed"
    GENERAL_ERROR = "An error occurred"
