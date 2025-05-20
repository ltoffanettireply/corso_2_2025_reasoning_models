from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import datetime

# Definisci il percorso del database
DATABASE_URL = "sqlite:///./reviews.db"

# Crea un'istanza del motore di database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crea una classe base per i modelli
Base = declarative_base()

# Crea una sessione per interagire con il database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definisci i modelli di database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    # Campi per il reset della password
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relazione con le recensioni (opzionale per ora)
    # reviews = relationship("Review", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"

# Definisci i modelli di database
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relazione con i prodotti
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    image = Column(String, nullable=True)
    
    # Chiave esterna per la categoria
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Relazioni
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # Titolo
    model = Column(String, index=True)  # Modello
    user = Column(String)               # User
    rating = Column(Integer)            # Rating (da 1 a 5 stelle)
    description = Column(Text)          # Descrizione testuale
    created_at = Column(DateTime, default=datetime.datetime.now)  # Use local time
    
    # Chiave esterna per il prodotto
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Relazioni
    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.title} by {self.user}>"


# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Crea le tabelle nel database
def create_tables():
    Base.metadata.create_all(bind=engine)


# Inizializza il database con alcune categorie iniziali
def init_db():
    db = SessionLocal()
    try:
        # Controlla se ci sono già categorie nel database
        if db.query(Category).count() == 0:
            # Aggiungi categorie iniziali
            categories = [
                Category(name="Smartphone", description="Dispositivi mobili e accessori"),
                Category(name="Computer", description="Laptop, desktop e accessori"),
                Category(name="Audio", description="Cuffie, speaker e dispositivi audio")
            ]
            db.add_all(categories)
            db.commit()
    finally:
        db.close()

def migrate_database():
    """Aggiunge colonne mancanti alle tabelle esistenti."""
    import sqlite3
    
    # Crea una connessione diretta al database
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    
    try:
        # Controlla se la colonna reset_token esiste nella tabella users
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Aggiungi la colonna reset_token se non esiste
        if "reset_token" not in columns:
            print("Aggiunta colonna reset_token alla tabella users")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
        
        # Aggiungi la colonna reset_token_expires se non esiste
        if "reset_token_expires" not in columns:
            print("Aggiunta colonna reset_token_expires alla tabella users")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP")
        
        # Salva le modifiche
        conn.commit()
    except Exception as e:
        print(f"Errore durante la migrazione del database: {e}")
    finally:
        conn.close()