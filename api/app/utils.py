# utils.py
import hashlib
from flask import current_app, render_template
from werkzeug.utils import secure_filename
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_mail import Message

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')

def verify_google_token(token):
    try:
        # Valide le token reçu de Google
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        
        # Si la validation réussit, retourne les informations utilisateur
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture')
        }
    except ValueError:
        # Si le token est invalide, retourne None
        return None

def validate_api_key(api_key):
    # Get the API key from app.config
    app_api_key = current_app.config.get('API_KEY')
    print(app_api_key)

    # Compare the api_key from the header with the one from app.config
    return api_key == app_api_key

def hash_password(password, salt):
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return hashed_password

def upload_img(image):
    # Check if the image is allowed
    if '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
        filename = secure_filename(image.filename)
        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return filename
    else:
        return None
    
def send_email(subject, recipients, template_name, **kwargs):
    """
    Envoie un email avec un template HTML en utilisant Flask-Mail.

    :param subject: Sujet de l'email
    :param recipients: Liste des destinataires de l'email
    :param template_name: Nom du template (sans l'extension .html)
    :param kwargs: Variables à passer au template
    """
    # Utilise le MAIL_USERNAME défini dans la configuration comme expéditeur
    sender = current_app.config.get('MAIL_USERNAME')

    # Crée le message de l'email
    msg = Message(subject, sender=sender, recipients=recipients)
    
    # Rendu du template HTML avec les variables
    msg.html = render_template(f"{template_name}.html", **kwargs)
    
    # Accès à Flask-Mail via current_app
    mail = current_app.extensions.get('mail')
    
    try:
        mail.send(msg)
        return True  # L'envoi a réussi
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email : {str(e)}")
        return str(e)
            
def send_welcome_email(recipient, name):
    subject = "Bienvenue sur notre plateforme"
    sender = MAIL_USERNAME
    
    # Utilisation de la fonction send_email avec le template welcome_email
    result = send_email(
        subject=subject,
        sender=sender,
        recipients=recipient,
        template_name="welcome_email",  # Le nom du template HTML sans l'extension
        name=name  # Variables à injecter dans le template
    )
    
    if result is True:
        return "Email sent successfully"
    else:
        return result
