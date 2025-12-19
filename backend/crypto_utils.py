import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()
FERNET_KEY = os.environ.get("FERNET_KEY")
cipher = Fernet(FERNET_KEY)

def encrypt_field(plain: str) -> str:
    
    return cipher.encrypt(plain.encode()).decode()

def decrypt_field(enc: str) -> str:
    
    return cipher.decrypt(enc.encode()).decode()
