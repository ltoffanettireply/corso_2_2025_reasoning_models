from sqlalchemy.orm import Session
from app import database, crud
import logging

def seed_sample_data():
    """Inserisce dati di esempio nel database."""
    logging.info("Inizializzazione dati di esempio nel database...")
    
    # Crea una sessione database
    db = database.SessionLocal()
    
    try:
        # Verifica se ci sono già dati nel database
        if db.query(database.Product).count() > 0:
            logging.info("I dati di esempio sono già presenti nel database.")
            return
        
        # Ottieni le categorie
        smartphone_category = db.query(database.Category).filter(database.Category.name == "Smartphone").first()
        computer_category = db.query(database.Category).filter(database.Category.name == "Computer").first()
        audio_category = db.query(database.Category).filter(database.Category.name == "Audio").first()
        
        if not smartphone_category or not computer_category or not audio_category:
            logging.error("Le categorie richieste non esistono nel database.")
            return
        
        # Crea prodotti di esempio per la categoria Smartphone
        smartphones = [
            {
                "name": "iPhone 15 Pro",
                "description": "Il nuovo flagship di Apple con fotocamera migliorata e chip A17 Pro. L'iPhone 15 Pro rappresenta l'eccellenza in termini di prestazioni e qualità fotografica, con un display Super Retina XDR da 6,1 pollici e il nuovo sistema di fotocamere Pro con sensore principale da 48MP.",
                "image": "iphone15pro.jpg",
                "category_id": smartphone_category.id
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "description": "Un concentrato di potenza con l'esclusiva S Pen e Galaxy AI. Il Galaxy S24 Ultra è dotato di un display Dynamic AMOLED 2X da 6,8 pollici e un sistema di fotocamere con zoom ottico 10x. La nuova S Pen e le funzioni di intelligenza artificiale lo rendono un dispositivo estremamente versatile.",
                "image": "s24ultra.jpg",
                "category_id": smartphone_category.id
            },
            {
                "name": "Google Pixel 8",
                "description": "L'esperienza Android più pura con incredibili capacità fotografiche. Il Pixel 8 combina il meglio di Google in un dispositivo elegante, con elaborazione computazionale delle immagini senza pari e il potente chip Tensor G3 per un'esperienza AI superiore.",
                "image": "pixel8.jpg",
                "category_id": smartphone_category.id
            }
        ]
        
        # Crea prodotti di esempio per la categoria Computer
        computers = [
            {
                "name": "MacBook Air M3",
                "description": "Leggero, silenzioso e potentissimo con il nuovo chip Apple Silicon. Il MacBook Air con chip M3 offre prestazioni eccezionali in un design incredibilmente sottile, con un'autonomia che può durare fino a 18 ore e un display Liquid Retina che supporta un miliardo di colori.",
                "image": "macbookair.jpg",
                "category_id": computer_category.id
            },
            {
                "name": "Dell XPS 15",
                "description": "Potente laptop con display InfinityEdge e prestazioni di livello professionale. L'XPS 15 combina un display quasi senza bordi con processori Intel di ultima generazione e schede grafiche NVIDIA, il tutto in un chassis in alluminio e fibra di carbonio.",
                "image": "placeholder.jpg",
                "category_id": computer_category.id
            }
        ]
        
        # Crea prodotti di esempio per la categoria Audio
        audio_products = [
            {
                "name": "Sony WH-1000XM5",
                "description": "La cancellazione del rumore più avanzata in cuffie confortevoli. Le WH-1000XM5 rappresentano lo stato dell'arte nella cancellazione del rumore, con otto microfoni e due processori che analizzano il suono 4000 volte al secondo per un'esperienza di ascolto immersiva.",
                "image": "sonywh1000xm5.jpg",
                "category_id": audio_category.id
            },
            {
                "name": "Apple AirPods Pro 2",
                "description": "Cancellazione attiva del rumore, audio spaziale e grande autonomia. Gli AirPods Pro di seconda generazione offrono un'esperienza audio personalizzata con cancellazione del rumore adattiva e modalità trasparenza per restare connessi con l'ambiente circostante.",
                "image": "placeholder.jpg",
                "category_id": audio_category.id
            }
        ]
        
        # Inserisci i prodotti nel database
        all_products = []
        for product_data in smartphones + computers + audio_products:
            product = database.Product(
                name=product_data["name"],
                description=product_data["description"],
                image=product_data["image"],
                category_id=product_data["category_id"]
            )
            db.add(product)
            all_products.append(product)
        
        db.commit()
        
        # Ricarica i prodotti per ottenere gli ID assegnati
        db.refresh_all(all_products)
        
        # Crea alcune recensioni di esempio
        reviews = [
            {
                "title": "Fotocamera incredibile!",
                "content": "Ho acquistato l'iPhone 15 Pro principalmente per le sue capacità fotografiche e non sono rimasto deluso. La qualità delle foto, soprattutto in condizioni di scarsa illuminazione, è semplicemente straordinaria. Il nuovo sensore da 48MP fa davvero la differenza rispetto al modello precedente.",
                "rating": 4.8,
                "author": "Marco B.",
                "product": smartphones[0]["name"]
            },
            {
                "title": "La S Pen è un game-changer",
                "content": "Uso il Galaxy S24 Ultra da un mese e la S Pen mi ha cambiato il modo di interagire con il telefono. È incredibilmente precisa e le funzioni di produttività sono eccellenti. L'unico neo è la durata della batteria che potrebbe essere migliore con un uso intensivo.",
                "rating": 4.6,
                "author": "Laura M.",
                "product": smartphones[1]["name"]
            },
            {
                "title": "Leggerezza e potenza in un unico dispositivo",
                "content": "Il MacBook Air M3 è esattamente ciò che cercavo: un laptop leggero che posso portare ovunque ma che non sacrifica le prestazioni. Riesco a fare editing video senza problemi e la batteria dura davvero tutto il giorno. L'assenza di ventole lo rende completamente silenzioso, anche sotto carico.",
                "rating": 5.0,
                "author": "Giovanni T.",
                "product": computers[0]["name"]
            },
            {
                "title": "Il meglio dell'audio wireless",
                "content": "Le Sony WH-1000XM5 sono le migliori cuffie che abbia mai provato. La cancellazione del rumore è così efficace che sembra di essere in una bolla di silenzio. La qualità audio è cristallina e il comfort è eccezionale anche dopo ore di utilizzo. L'app di controllo offre molte possibilità di personalizzazione.",
                "rating": 4.9,
                "author": "Alessia F.",
                "product": audio_products[0]["name"]
            }
        ]
        
        # Ottieni i prodotti dal database
        products_dict = {}
        for product in all_products:
            products_dict[product.name] = product.id
        
        # Inserisci le recensioni nel database
        for review_data in reviews:
            product_id = products_dict.get(review_data["product"])
            if product_id:
                review = database.Review(
                    title=review_data["title"],
                    content=review_data["content"],
                    rating=review_data["rating"],
                    author=review_data["author"],
                    product_id=product_id
                )
                db.add(review)
        
        db.commit()
        logging.info("Dati di esempio inseriti con successo nel database!")
    
    except Exception as e:
        db.rollback()
        logging.error(f"Errore nell'inizializzazione dei dati di esempio: {e}")
    
    finally:
        db.close()
