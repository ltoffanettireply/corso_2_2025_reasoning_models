from sqlalchemy.orm import Session
from . import database, schemas
from .security import get_password_hash, verify_password
from typing import List, Optional
import datetime
import secrets


# Funzioni per le categorie
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Category).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int):
    return db.query(database.Category).filter(database.Category.id == category_id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(database.Category).filter(database.Category.name == name).first()


# Funzioni per i prodotti
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Product).offset(skip).limit(limit).all()


def get_products_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 100):
    return db.query(database.Product).filter(database.Product.category_id == category_id).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(database.Product).filter(database.Product.id == product_id).first()


def create_product(db: Session, name: str, description: str, category_id: int, image: Optional[str] = None):
    db_product = database.Product(name=name, description=description, category_id=category_id, image=image)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Funzioni per le recensioni
def get_reviews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Review).offset(skip).limit(limit).all()


def get_product_reviews(db: Session, product_id: int, skip: int = 0, limit: int = 100, sort_by: str = None):
    """
    Ottiene le recensioni di un prodotto con opzioni di ordinamento:
    - rating_asc: valutazioni in ordine crescente
    - rating_desc: valutazioni in ordine decrescente (default)
    - date_asc: data in ordine crescente (più vecchie prime)
    - date_desc: data in ordine decrescente (più recenti prime)
    """
    query = db.query(database.Review).filter(database.Review.product_id == product_id)
    
    # Applica l'ordinamento in base al parametro sort_by
    if sort_by == "rating_asc":
        query = query.order_by(database.Review.rating.asc())
    elif sort_by == "rating_desc":
        query = query.order_by(database.Review.rating.desc())
    elif sort_by == "date_asc":
        query = query.order_by(database.Review.created_at.asc())
    elif sort_by == "date_desc":
        query = query.order_by(database.Review.created_at.desc())
    else:
        # Default: recensioni più recenti prime
        query = query.order_by(database.Review.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_review(db: Session, review_id: int):
    return db.query(database.Review).filter(database.Review.id == review_id).first()


def create_review(db: Session, title: str, model: str, user: str, rating: int, description: str, product_id: int):
    # Import locally to avoid circular imports
    from .datetime_utils import get_local_datetime
    
    db_review = database.Review(
        title=title,
        model=model,
        user=user,
        rating=rating,
        description=description,
        product_id=product_id,
        created_at=get_local_datetime()  # Use local time from utility function
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


# Funzionalità di update e delete review rimosse perché non utilizzate


# Funzioni di utility
def get_featured_reviews(db: Session, limit: int = 12):
    """Ottiene le recensioni più recenti o in evidenza"""
    return db.query(database.Review).order_by(database.Review.created_at.desc()).limit(limit).all()

# Funzioni per gli utenti
def get_user_by_email(db: Session, email: str):
    """Ottiene un utente tramite email"""
    return db.query(database.User).filter(database.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Ottiene un utente tramite username"""
    return db.query(database.User).filter(database.User.username == username).first()

def get_user(db: Session, user_id: int):
    """Ottiene un utente tramite ID"""
    return db.query(database.User).filter(database.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Crea un nuovo utente"""
    hashed_password = get_password_hash(user.password)
    db_user = database.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """Autentica un utente verificando username e password"""
    user = get_user_by_username(db, username)
    if not user:
        # Prova con l'email
        user = get_user_by_email(db, username)
        if not user:
            return False
    
    if not verify_password(password, user.hashed_password):
        return False
    
    return user


def generate_password_reset_token(db: Session, email: str):
    """Genera un token di reset password per l'utente con l'email specificata"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Genera un token univoco
    token = secrets.token_urlsafe(32)
    
    # Imposta la scadenza a 30 minuti da adesso
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)
    
    # Salva il token e la scadenza nel database
    user.reset_token = token
    user.reset_token_expires = expiry
    db.commit()
    
    return token

def verify_reset_token(db: Session, token: str):
    """Verifica se il token è valido e restituisce l'utente associato"""
    now = datetime.datetime.now()
    
    # Cerca l'utente con questo token
    user = db.query(database.User).filter(
        database.User.reset_token == token,
        database.User.reset_token_expires > now
    ).first()
    
    return user

def reset_password(db: Session, token: str, new_password: str):
    """Reimposta la password dell'utente usando il token"""
    user = verify_reset_token(db, token)
    if not user:
        return False
    
    # Aggiorna la password
    user.hashed_password = get_password_hash(new_password)
    
    # Invalida il token
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()
    return True