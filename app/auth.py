"""
Authentication and user management for Hope's Caramels Traceability System.
"""
from .data import USERS_PATH, save_json, timestamp_now
from .utils import generate_user_id
from typing import List, Dict, Any, Tuple

def authenticate_user(email: str, password: str, users: List[Dict[str, Any]]) -> Any:
    for user in users:
        if user["email"].lower() == email.lower() and user["password"] == password:
            return user
    return None

def register_user(full_name: str, email: str, password: str, role: str, users: List[Dict[str, Any]]) -> Tuple[bool, str]:
    for user in users:
        if user["email"].lower() == email.lower():
            return False, "An account with this email already exists."
    new_user = {
        "id": generate_user_id(users),
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
        "created_at": timestamp_now()
    }
    users.append(new_user)
    save_json(USERS_PATH, users)
    return True, "Registration successful."
