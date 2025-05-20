import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Configurazione di base per l'invio delle email
EMAIL_HOST = os.environ.get("EMAIL_HOST")  # Ottenere l'host SMTP da variabile d'ambiente
EMAIL_PORT = os.environ.get("EMAIL_PORT")  # Ottenere la porta SMTP da variabile d'ambiente
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")  # Ottenere l'email da variabile d'ambiente
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # Ottenere la password da variabile d'ambiente
EMAIL_FROM = f"Tech Reviews <{EMAIL_USERNAME}>"

# Per l'ambiente di sviluppo, stampa solo le email invece di inviarle
# In ambiente di produzione questo deve essere False
DEBUG_MODE = os.environ.get("DEBUG_MODE").lower() == "true"

def send_email(to_email, subject, html_content):
    """
    Invia un'email con contenuto HTML.
    Se DEBUG_MODE è True, stampa solo il contenuto dell'email.
    """
    if DEBUG_MODE:
        print(f"\n--- DEBUG: EMAIL NON INVIATA ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Content: {html_content}")
        print(f"--- FINE DEBUG EMAIL ---\n")
        return True
    
    try:
        # Configura il messaggio
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        
        # Aggiungi il corpo HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Connessione al server SMTP
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Errore nell'invio dell'email: {e}")
        return False

def send_password_reset_email(user_email, username, reset_token, base_url):
    """
    Invia un'email per il reset della password.
    """
    reset_url = f"{base_url}/reset-password/{reset_token}"
    
    subject = "Reset della password per Tech Reviews"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .button {{ display: inline-block; background-color: #3498db; color: #ffffff !important; padding: 12px 24px; 
                       text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Tech Reviews</h1>
            </div>
            <div class="content">
                <h2>Ciao {username},</h2>
                <p>Abbiamo ricevuto una richiesta per reimpostare la password del tuo account Tech Reviews.</p>
                <p>Per reimpostare la tua password, fai clic sul pulsante qui sotto:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reimposta Password</a>
                </p>
                <p>Oppure copia e incolla questo link nel tuo browser:</p>
                <p>{reset_url}</p>
                <p>Il link sarà valido per 30 minuti. Se non hai richiesto il reset della password, puoi ignorare questa email.</p>
                <p>Cordiali saluti,<br>Il team di Tech Reviews</p>
            </div>
            <div class="footer">
                <p>Questa email è stata inviata a {user_email} perché è stato richiesto un reset della password.</p>
                <p>&copy; 2025 Tech Reviews - Tutti i diritti riservati</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, html_content)


def send_newsletter_subscription_confirmation(email, unsubscribe_token, base_url):
    """
    Invia un'email di conferma dell'iscrizione alla newsletter.
    """
    unsubscribe_url = f"{base_url}/unsubscribe/{unsubscribe_token}"
    
    subject = "Benvenuto alla Newsletter di Tech Reviews"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .button {{ display: inline-block; background-color: #3498db; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            .unsubscribe {{ font-size: 11px; color: #999; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Tech Reviews</h1>
            </div>
            <div class="content">
                <h2>Grazie per l'iscrizione!</h2>
                <p>La tua iscrizione alla newsletter di Tech Reviews è stata confermata.</p>
                <p>Riceverai aggiornamenti sulle ultime recensioni di prodotti tech pubblicate sul nostro sito.</p>
                <p>Cordiali saluti,<br>Il team di Tech Reviews</p>
            </div>
            <div class="footer">
                <p class="unsubscribe">Se non desideri più ricevere le nostre email, <a href="{unsubscribe_url}">clicca qui per disiscriverti</a>.</p>
                <p>&copy; 2025 Tech Reviews - Tutti i diritti riservati</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)


def send_new_review_notification(subscriber_email, review, product, base_url, unsubscribe_token):
    """
    Invia una notifica di nuova recensione agli iscritti alla newsletter.
    """
    product_url = f"{base_url}/product/{product.id}"
    unsubscribe_url = f"{base_url}/unsubscribe/{unsubscribe_token}"
    
    subject = f"Nuova Recensione: {review.title}"
    
    # Crea una versione abbreviata della descrizione per l'anteprima
    short_description = review.description[:150] + '...' if len(review.description) > 150 else review.description
    
    # Genera il contenuto HTML dell'email
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .review-info {{ margin: 15px 0; }}
            .rating {{ color: #f39c12; font-weight: bold; }}
            .button {{ display: inline-block; background-color: #3498db; color: #ffffff !important; padding: 12px 24px; 
                       text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            .unsubscribe {{ font-size: 11px; color: #999; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Tech Reviews</h1>
            </div>
            <div class="content">
                <h2>Nuova Recensione Pubblicata</h2>
                <div class="review-info">
                    <h3>{review.title}</h3>
                    <p>Prodotto: <strong>{review.model}</strong></p>
                    <p>Valutazione: <span class="rating">{'★' * review.rating}{'☆' * (5-review.rating)}</span> {review.rating}/5</p>
                    <p>Autore: {review.user}</p>
                    <p>{short_description}</p>
                </div>
                <p style="text-align: center;">
                    <a href="{product_url}" class="button">Visualizza la recensione sul nostro sito</a>
                </p>
            </div>
            <div class="footer">
                <p class="unsubscribe">Se non desideri più ricevere le nostre email, <a href="{unsubscribe_url}">clicca qui per disiscriverti</a>.</p>
                <p>&copy; 2025 Tech Reviews - Tutti i diritti riservati</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subscriber_email, subject, html_content)