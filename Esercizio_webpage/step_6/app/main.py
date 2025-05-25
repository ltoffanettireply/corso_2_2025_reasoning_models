from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from pydantic import EmailStr

from . import crud, database, schemas
from .security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, verify_password
from .email_service import send_password_reset_email, send_newsletter_subscription_confirmation, send_new_review_notification


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
    database.create_tables()
    database.init_db()

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

# Rotta per la disiscrizione dalla newsletter (reindirizza all'API)
@app.get("/unsubscribe/{token}", response_class=RedirectResponse)
async def unsubscribe_redirect(token: str):
    return RedirectResponse(url=f"/api/newsletter/unsubscribe/{token}", status_code=303)

# Rotte per i prodotti
@app.get("/api/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

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
        "user": current_user  # Passa l'utente al template
    })

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
async def login_page(request: Request, next: str = None, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente è già autenticato, reindirizza alla pagina richiesta o alla home
    if current_user:
        if next:
            return RedirectResponse(url=next, status_code=303)
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "page_title": "Accedi - Tech Reviews",
        "user": None,
        "next": next  # Passa il parametro next al template
    })

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...),
    next: str = Form(None),
    db: Session = Depends(get_db)
):
    # Autentica l'utente (usando l'email come username)
    user = crud.authenticate_user(db, email, password)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "page_title": "Accedi - Tech Reviews",
            "error": "Email o password non validi.",
            "next": next
        })
    
    # Crea un token di accesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Imposta il cookie e reindirizza
    if next:
        response = RedirectResponse(url=next, status_code=303)
    else:
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
    
    # Ottieni le recensioni dell'utente
    user_reviews = crud.get_user_reviews(db, current_user.username)
    
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "page_title": "Profilo - Tech Reviews",
        "user": current_user,
        "user_reviews": user_reviews
    })
    
@app.get("/edit_review/{review_id}", response_class=HTMLResponse)
async def edit_review_page(review_id: int, request: Request, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Ottieni la recensione
    review = crud.get_review(db, review_id)
    
    # Verifica che la recensione esista e che appartenga all'utente corrente
    if not review:
        raise HTTPException(status_code=404, detail="Recensione non trovata")
        
    if review.user != current_user.username:
        raise HTTPException(status_code=403, detail="Non hai il permesso di modificare questa recensione")
    
    # Mostra il form di modifica
    return templates.TemplateResponse("edit-review.html", {
        "request": request,
        "page_title": f"Modifica Recensione - {review.title}",
        "user": current_user,
        "review": review
    })
    
@app.post("/edit_review/{review_id}", response_class=HTMLResponse)
async def edit_review(
    review_id: int,
    request: Request,
    title: str = Form(...),
    rating: int = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Ottieni la recensione
    review = crud.get_review(db, review_id)
    
    # Verifica che la recensione esista e che appartenga all'utente corrente
    if not review:
        raise HTTPException(status_code=404, detail="Recensione non trovata")
        
    if review.user != current_user.username:
        raise HTTPException(status_code=403, detail="Non hai il permesso di modificare questa recensione")
    
    # Aggiorna la recensione
    updated_review = crud.update_review(db, review_id, title, rating, description)
    
    # Reindirizza alla pagina del profilo
    return RedirectResponse(url="/profile", status_code=303)

@app.post("/delete_review/{review_id}", response_class=RedirectResponse)
async def delete_review(request: Request, review_id: int, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Ottieni la recensione
    review = crud.get_review(db, review_id)
    
    # Verifica che la recensione esista e che appartenga all'utente corrente
    if review and review.user == current_user.username:
        # Elimina la recensione
        crud.delete_review(db, review_id)
    
    # Reindirizza alla pagina del profilo
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {
        "request": request,
        "page_title": "Password dimenticata - Tech Reviews"
    })

@app.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    # Verifica se l'email esiste nel database
    user = crud.get_user_by_email(db, email)
    
    if not user:
        return templates.TemplateResponse("forgot-password.html", {
            "request": request,
            "page_title": "Password dimenticata - Tech Reviews",
            "error": "Nessun account registrato con questa email."
        })
    
    # Genera un token di reset
    token = crud.generate_password_reset_token(db, email)
    
    # Costruisci l'URL base
    base_url = str(request.base_url).rstrip('/')
    
    # Invia l'email di reset
    email_sent = send_password_reset_email(
        user_email=user.email,
        username=user.username,
        reset_token=token,
        base_url=base_url
    )
    
    if not email_sent:
        return templates.TemplateResponse("forgot-password.html", {
            "request": request,
            "page_title": "Password dimenticata - Tech Reviews",
            "error": "Errore nell'invio dell'email. Riprova più tardi."
        })
    
    return templates.TemplateResponse("forgot-password.html", {
        "request": request,
        "page_title": "Password dimenticata - Tech Reviews",
        "success": "Abbiamo inviato un'email con istruzioni per reimpostare la tua password."
    })

@app.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    # Verifica se il token è valido
    user = crud.verify_reset_token(db, token)
    
    if not user:
        return templates.TemplateResponse("reset-password.html", {
            "request": request,
            "page_title": "Reset Password - Tech Reviews",
            "error": "Il link di reset non è valido o è scaduto.",
            "token": token
        })
    
    return templates.TemplateResponse("reset-password.html", {
        "request": request,
        "page_title": "Reset Password - Tech Reviews",
        "token": token
    })

@app.post("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password(
    request: Request, 
    token: str, 
    password: str = Form(...), 
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verifica la corrispondenza delle password
    if password != confirm_password:
        return templates.TemplateResponse("reset-password.html", {
            "request": request,
            "page_title": "Reset Password - Tech Reviews",
            "error": "Le password non corrispondono.",
            "token": token
        })
    
    # Verifica se il token è valido
    user = crud.verify_reset_token(db, token)

    if not user:
        return templates.TemplateResponse("reset-password.html", {
            "request": request,
            "page_title": "Reset Password - Tech Reviews",
            "error": "Il link di reset non è valido o è scaduto.",
            "token": token
        })
    
    # Reimposta la password
    success = crud.reset_password(db, token, password)
    
    if not success:
        return templates.TemplateResponse("reset-password.html", {
            "request": request,
            "page_title": "Reset Password - Tech Reviews",
            "error": "Si è verificato un errore. Riprova più tardi.",
            "token": token
        })
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "page_title": "Accedi - Tech Reviews",
        "success": "Password reimpostata con successo! Ora puoi accedere con la tua nuova password.",
        "user": None
    })

@app.get("/profile/edit", response_class=HTMLResponse)
async def edit_profile_page(request: Request, db: Session = Depends(get_db)):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("profile-edit.html", {
        "request": request, 
        "page_title": "Modifica Profilo - Tech Reviews",
        "user": current_user
    })

@app.post("/profile/edit/email", response_class=HTMLResponse)
async def update_email(
    request: Request, 
    new_email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verifica la password
    if not verify_password(password, current_user.hashed_password):
        return templates.TemplateResponse("profile-edit.html", {
            "request": request,
            "page_title": "Modifica Profilo - Tech Reviews",
            "user": current_user,
            "error_email": "Password non corretta"
        })
    
    # Aggiorna l'email
    success, message = crud.update_user_email(db, current_user.id, new_email)
    
    if success:
        # Forza il logout e reindirizza all'accesso (l'utente deve accedere nuovamente)
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(key="access_token")
        return response
    else:
        return templates.TemplateResponse("profile-edit.html", {
            "request": request,
            "page_title": "Modifica Profilo - Tech Reviews",
            "user": current_user,
            "error_email": message
        })

@app.post("/profile/edit/password", response_class=HTMLResponse)
async def update_password(
    request: Request, 
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verifica che le nuove password corrispondano
    if new_password != confirm_password:
        return templates.TemplateResponse("profile-edit.html", {
            "request": request,
            "page_title": "Modifica Profilo - Tech Reviews",
            "user": current_user,
            "error_password": "Le nuove password non corrispondono"
        })
    
    # Aggiorna la password
    success, message = crud.update_user_password(db, current_user.id, current_password, new_password)
    
    if success:
        return templates.TemplateResponse("profile-edit.html", {
            "request": request,
            "page_title": "Modifica Profilo - Tech Reviews",
            "user": current_user,
            "success_password": message
        })
    else:
        return templates.TemplateResponse("profile-edit.html", {
            "request": request,
            "page_title": "Modifica Profilo - Tech Reviews",
            "user": current_user,
            "error_password": message
        })
 
 # Aggiungi questa route dopo le altre route GET
@app.get("/submit-review", response_class=HTMLResponse)
async def submit_review_page(
    request: Request, 
    product_id: int = None,
    back_url: str = None,
    db: Session = Depends(get_db)
):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url=f"/login?next=/submit-review{f'?product_id={product_id}' if product_id else ''}", status_code=303)
    
    # Recupera tutte le categorie
    categories = crud.get_categories(db)
    
    # Recupera informazioni sul prodotto iniziale, se specificato
    initial_product_name = None
    initial_category_id = None
    if product_id:
        product = crud.get_product(db, product_id)
        if product:
            initial_product_name = product.name
            initial_category_id = product.category_id
    
    return templates.TemplateResponse("submit-review.html", {
        "request": request,
        "page_title": "Scrivi Recensione - Tech Reviews",
        "user": current_user,
        "categories": categories,
        "initial_product_name": initial_product_name,
        "initial_category_id": initial_category_id
    })

# Aggiungi questa route dopo le altre route POST
@app.post("/submit-review", response_class=HTMLResponse)
async def submit_review(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    product_name: str = Form(...),
    category_id: int = Form(...),
    rating: int = Form(...),
    user: str = Form(...),
    db: Session = Depends(get_db)
):
    # Ottieni l'utente corrente
    current_user = await get_current_user_from_cookie(request, db)
    
    # Se l'utente non è autenticato, reindirizza alla pagina di login
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verifica che l'username corrisponda all'utente corrente
    if user != current_user.username:
        return templates.TemplateResponse("submit-review.html", {
            "request": request,
            "page_title": "Scrivi Recensione - Tech Reviews",
            "user": current_user,
            "categories": crud.get_categories(db),
            "review_title": title,
            "review_description": description,
            "initial_product_name": product_name,
            "review_rating": rating,
            "initial_category_id": category_id,
            "error": "C'è stato un problema con l'autenticazione. Riprova."
        })
    
    try:
        # Verifica se il prodotto esiste già
        product = None
        # Cerca prima un prodotto con nome esatto
        products = crud.get_products(db)
        for p in products:
            if p.name.lower() == product_name.lower() and p.category_id == category_id:
                product = p
                break
        
        # Se il prodotto non esiste, crealo
        if not product:
            product = crud.create_product(
                db=db,
                name=product_name,
                description=f"Prodotto {product_name}",
                category_id=category_id
            )
        
        # Crea la recensione
        review = crud.create_review(
            db=db,
            title=title,
            model=product_name,  # Usa il nome del prodotto come modello
            user=user,
            rating=rating,
            description=description,
            product_id=product.id
        )
        
        # Invia notifiche agli iscritti alla newsletter
        subscribers = crud.get_active_newsletter_subscribers(db)
        base_url = str(request.base_url).rstrip('/')
        
        # Invia email a tutti gli abbonati
        for subscriber in subscribers:
            send_new_review_notification(
                subscriber_email=subscriber.email, 
                review=review,
                product=product,
                base_url=base_url,
                unsubscribe_token=subscriber.unsubscribe_token
            )
        
        return RedirectResponse(url=f"/product/{product.id}", status_code=303)
    
    except Exception as e:
        # In caso di errore, ritorna alla pagina del form con un messaggio
        return templates.TemplateResponse("submit-review.html", {
            "request": request,
            "page_title": "Scrivi Recensione - Tech Reviews",
            "user": current_user,
            "categories": crud.get_categories(db),
            "review_title": title,
            "review_description": description,
            "initial_product_name": product_name,
            "review_rating": rating,
            "initial_category_id": category_id,
            "error": f"Si è verificato un errore: {str(e)}"
        })
    
@app.post("/api/newsletter/subscribe", response_model=Dict[str, Any])
async def subscribe_to_newsletter(
    request: Request,
    subscriber: schemas.NewsletterSubscriberCreate,
    db: Session = Depends(database.get_db)
):
    # Verifica se l'email è già iscritta
    existing_subscriber = crud.get_subscriber_by_email(db, subscriber.email)
    
    if existing_subscriber:
        # Se l'abbonato esiste ma non è attivo, lo riattiviamo
        if not existing_subscriber.is_active:
            # Riattiva l'abbonamento
            subscriber_obj = crud.subscribe_to_newsletter(db, subscriber.email)
            
            # Invia email di conferma
            base_url = str(request.base_url).rstrip('/')
            send_newsletter_subscription_confirmation(
                email=subscriber_obj.email,
                unsubscribe_token=subscriber_obj.unsubscribe_token,
                base_url=base_url
            )
            
            return {"success": True, "message": "Iscrizione alla newsletter attivata nuovamente!"}
        
        # Se è già attivo, restituiamo un messaggio
        return {"success": True, "message": "Sei già iscritto alla nostra newsletter!"}
    
    try:
        # Crea un nuovo abbonato
        subscriber_obj = crud.subscribe_to_newsletter(db, subscriber.email)
        
        # Invia email di conferma
        base_url = str(request.base_url).rstrip('/')
        send_newsletter_subscription_confirmation(
            email=subscriber_obj.email,
            unsubscribe_token=subscriber_obj.unsubscribe_token,
            base_url=base_url
        )
        
        return {"success": True, "message": "Grazie per l'iscrizione alla newsletter!"}
    except Exception as e:
        return {"success": False, "message": f"Si è verificato un errore: {str(e)}"}

# Endpoint per la disiscrizione dalla newsletter
@app.get("/api/newsletter/unsubscribe/{token}", response_class=HTMLResponse)
async def unsubscribe_from_newsletter(
    request: Request, 
    token: str, 
    db: Session = Depends(database.get_db)
):
    # Cerca il subscriber con il token specificato
    subscriber = crud.get_subscriber_by_token(db, token)
    
    if not subscriber:
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Token di disiscrizione non valido</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: center; padding: 50px; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                    h1 { color: #e74c3c; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Token di disiscrizione non valido</h1>
                    <p>Il link che hai utilizzato non è valido o è scaduto.</p>
                    <p><a href="/">Torna alla home</a></p>
                </div>
            </body>
        </html>
        """)
    
    # Disiscrive l'utente
    success = crud.unsubscribe_from_newsletter(db, token)
    
    if success:
        return HTMLResponse(content=f"""
        <html>
            <head>
                <title>Disiscrizione completata</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: center; padding: 50px; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                    h1 {{ color: #3498db; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Disiscrizione completata</h1>
                    <p>La tua email <strong>{subscriber.email}</strong> è stata rimossa dalla nostra newsletter.</p>
                    <p>Non riceverai più email da parte nostra. Se cambi idea, puoi sempre iscriverti nuovamente dalla nostra home page.</p>
                    <p><a href="/">Torna alla home</a></p>
                </div>
            </body>
        </html>
        """)
    else:
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Errore nella disiscrizione</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: center; padding: 50px; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                    h1 { color: #e74c3c; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Errore nella disiscrizione</h1>
                    <p>Si è verificato un errore durante la disiscrizione. Riprova più tardi o contatta l'assistenza.</p>
                    <p><a href="/">Torna alla home</a></p>
                </div>
            </body>
        </html>
        """)
