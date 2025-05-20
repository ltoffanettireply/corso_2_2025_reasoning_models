from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


# Schemi per le categorie
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


# Schemi per i prodotti
class ProductBase(BaseModel):
    name: str
    description: str
    category_id: int
    image: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True


# Schemi per le recensioni
class ReviewBase(BaseModel):
    title: str  # Titolo
    model: str  # Modello
    user: str   # User
    rating: int = Field(..., ge=1, le=5)  # Rating (da 1 a 5 stelle)
    description: str  # Descrizione testuale


class ReviewCreate(ReviewBase):
    product_id: int


class Review(ReviewBase):
    id: int
    created_at: datetime
    product_id: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=None).isoformat()
        }


# Schemi per le risposte API
class ProductWithReviews(Product):
    reviews: List[Review] = []
    
    class Config:
        from_attributes = True


class CategoryWithProducts(Category):
    products: List[Product] = []
    
    class Config:
        from_attributes = True

# Schemi per gli utenti
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Schemi per token di autenticazione
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
  
    
# Schemi per la newsletter
class NewsletterSubscriberBase(BaseModel):
    email: EmailStr


class NewsletterSubscriberCreate(NewsletterSubscriberBase):
    pass


class NewsletterSubscriber(NewsletterSubscriberBase):
    id: int
    is_active: bool
    created_at: datetime
    unsubscribe_token: str
    
    class Config:
        from_attributes = True
