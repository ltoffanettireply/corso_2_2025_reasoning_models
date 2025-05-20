from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from pydantic import EmailStr

from . import crud, database, schemas
from .security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

# Crea le tabelle del database all'avvio
database.create_tables()

app = FastAPI(title="Tech Reviews")

# Configura il middleware per servire i file statici
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")
favicon_path = os.path.join(static_dir, "favicon", "favicon.ico")

# Dipendenza per ottenere la sessione del database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configurazione OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funzione per ottenere l'utente corrente dalle credenziali
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configura i template
templates = Jinja2Templates(directory=templates_dir)

# Aggiungi route per favicon e altri file comuni del browser
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

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
    
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "page_title": "Tech Reviews - Le migliori recensioni di prodotti tecnologici",
        "featured_reviews": featured_reviews,
        "user": current_user
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
    
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    return templates.TemplateResponse("category.html", {
        "request": request,
        "page_title": f"{category.name} - Tech Reviews",
        "category": category,
        "products": products,
        "user": current_user  # Aggiungi l'utente al contesto
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
    
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    return templates.TemplateResponse("product.html", {
        "request": request,
        "page_title": f"{product.name} - Tech Reviews",
        "product": product,
        "reviews": reviews,
        "sort": sort,
        "sort_options": sort_options,
        "current_sort_name": current_sort_name,
        "user": current_user  # Aggiungi l'utente al contesto
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente è già autenticato, reindirizza alla home
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse("register.html", {
        "request": request, 
        "page_title": "Registrati - Tech Reviews",
        "user": None
    })

@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request, 
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Controlla se le password corrispondono
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "page_title": "Registrati - Tech Reviews",
            "error": "Le password non corrispondono."
        })

    # Controlla se l'email esiste già
    user_email = crud.get_user_by_email(db, email)
    if user_email:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "page_title": "Registrati - Tech Reviews",
            "error": "Email già registrata."
        })
    
    # Controlla se lo username esiste già
    user_username = crud.get_user_by_username(db, username)
    if user_username:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "page_title": "Registrati - Tech Reviews",
            "error": "Username già in uso."
        })
    
    # Crea il nuovo utente
    user_create = schemas.UserCreate(
        username=username,
        email=email,
        password=password
    )
    user = crud.create_user(db, user_create)
    
    # Mostra un messaggio di successo
    return templates.TemplateResponse("register.html", {
        "request": request,
        "page_title": "Registrati - Tech Reviews",
        "success": "Registrazione completata con successo! Ora puoi accedere."
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente è già autenticato, reindirizza alla home
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "page_title": "Accedi - Tech Reviews",
        "user": None
    })

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Autentica l'utente (usando l'email come username)
    user = crud.authenticate_user(db, email, password)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "page_title": "Accedi - Tech Reviews",
            "error": "Email o password non validi."
        })
    
    # Crea un token di accesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Imposta il cookie o reindirizza con il token
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Il cookie non è accessibile via JavaScript
        max_age=1800,   # 30 minuti in secondi
        expires=1800,   # 30 minuti in secondi
    )
    
    return response

# Funzione per ottenere l'utente corrente dai cookie (per le pagine HTML)
async def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return None
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = crud.get_user_by_username(db, username=username)
        return user
    except JWTError:
        return None
    
@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "page_title": "Il tuo profilo - Tech Reviews",
        "user": current_user
    })

@app.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response