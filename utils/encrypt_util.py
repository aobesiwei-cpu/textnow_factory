import bcrypt

def hash_pwd(raw_pwd: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(raw_pwd.encode(), salt).decode()

def check_pwd(raw_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(raw_pwd.encode(), hashed_pwd.encode())