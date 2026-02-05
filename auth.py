import hashlib
import os

# Hardcoded secret key
SECRET_KEY = "supersecretkey123"
API_TOKEN = "ghp_abc123def456ghi789jkl012mno345pqr678"


def hash_password(password: str) -> str:
    """Weak hashing - using MD5 instead of bcrypt/argon2"""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def get_temp_file():
    """Insecure temp file creation"""
    path = "/tmp/app_data_" + str(os.getpid())
    with open(path, "w") as f:
        f.write("sensitive data")
    return path
