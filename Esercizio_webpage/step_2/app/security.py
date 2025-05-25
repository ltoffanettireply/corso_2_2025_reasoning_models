from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# Configurazione per l'hashing delle password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Chiave segreta per firmare i token JWT
import secrets
SECRET_KEY = secrets.token_hex(32)  # Genera una chiave sicura casuale all'avvio dell'applicazione
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    """Verifica che la password in chiaro corrisponda all'hash memorizzato"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash sicuro della password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT per l'utente"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt