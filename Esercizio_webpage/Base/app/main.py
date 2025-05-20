from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import os

from . import crud, database, schemas

# Crea le tabelle del database all'avvio
database.create_tables()

app = FastAPI(title="Tech Reviews")

# Configura il middleware per servire i file statici
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")
favicon_path = os.path.join(static_dir, "favicon", "favicon.ico")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Aggiungi route per favicon e altri file comuni del browser
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

# Configura i template
templates = Jinja2Templates(directory=templates_dir)

# Dipendenza per ottenere la sessione del database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inizializza il database con i dati iniziali
@app.on_event("startup")
def on_startup():
    database.init_db()
    
    # Importa e esegui la funzione di seed
    from app.seed import seed_sample_data
    seed_sample_data()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # Ottieni le recensioni in evidenza dal database (esplicitamente 12)
    featured_reviews = crud.get_featured_reviews(db, limit=12)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "page_title": "Tech Reviews - Le migliori recensioni di prodotti tecnologici",
        "featured_reviews": featured_reviews
    })

# Rotte per le categorie
# Nota: Le API seguenti sono definite per completezza e per potenziali sviluppi futuri,
# ma attualmente solo /api/reviews/ viene utilizzata direttamente dal frontend
@app.get("/api/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@app.get("/api/categories/{category_id}", response_model=schemas.CategoryWithProducts)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata")
    return db_category

# Rotte per i prodotti
@app.get("/api/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/api/products/{product_id}", response_model=schemas.ProductWithReviews)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    return db_product

@app.get("/api/categories/{category_id}/products", response_model=List[schemas.Product])
def read_category_products(category_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products_by_category(db, category_id=category_id, skip=skip, limit=limit)
    return products

# Rotte per le recensioni
@app.get("/api/reviews/", response_model=List[schemas.Review])
def read_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = crud.get_reviews(db, skip=skip, limit=limit)
    return reviews

@app.get("/api/products/{product_id}/reviews", response_model=List[schemas.Review])
def read_product_reviews(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = crud.get_product_reviews(db, product_id=product_id, skip=skip, limit=limit)
    return reviews

@app.post("/api/reviews/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    return crud.create_review(
        db=db,
        title=review.title,
        model=review.model,
        user=review.user,
        rating=review.rating,
        description=review.description,
        product_id=review.product_id
    )

# Rotte per le pagine web
@app.get("/category/{category_id}", response_class=HTMLResponse)
async def category_page(request: Request, category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata")
        
    products = crud.get_products_by_category(db, category_id)
    
    return templates.TemplateResponse("category.html", {
        "request": request,
        "page_title": f"{category.name} - Tech Reviews",
        "category": category,
        "products": products
    })

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_page(request: Request, product_id: int, sort: str = None, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
        
    # Ottieni le recensioni con l'ordinamento richiesto
    reviews = crud.get_product_reviews(db, product_id, sort_by=sort)
    
    # Mappa per i nomi visualizzati dell'ordinamento
    sort_options = {
        "rating_asc": "Valutazione (crescente)",
        "rating_desc": "Valutazione (decrescente)",
        "date_asc": "Data (crescente)",
        "date_desc": "Data (decrescente)",
        None: "Più recenti prima"
    }
    
    # Ottieni il nome visualizzato per l'ordinamento corrente
    current_sort_name = sort_options.get(sort, "Più recenti prima")
    
    return templates.TemplateResponse("product.html", {
        "request": request,
        "page_title": f"{product.name} - Tech Reviews",
        "product": product,
        "reviews": reviews,
        "sort": sort,
        "sort_options": sort_options,
        "current_sort_name": current_sort_name
    })
