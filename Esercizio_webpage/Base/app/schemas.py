from pydantic import BaseModel, Field
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
