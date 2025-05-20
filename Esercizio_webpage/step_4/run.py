import uvicorn

if __name__ == "__main__":
    print("Avvio del server Tech Reviews...")
    print("Accedi all'applicazione su http://127.0.0.1:8000")
    
    # Avvia il server con Uvicorn direttamente
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
