import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def envoyer_recap(texte, sujet="Récap bot trading (démo)"):
    adresse = os.getenv("GMAIL_ADRESSE")
    mot_de_passe = os.getenv("GMAIL_MOT_DE_PASSE")
    destinataire = os.getenv("EMAIL_DESTINATAIRE") or adresse
    if not adresse or not mot_de_passe:
        raise SystemExit("Identifiants Gmail introuvables : vérifie le fichier .env")

    message = EmailMessage()
    message["Subject"] = f"{sujet} - {datetime.now():%d/%m/%Y %H:%M}"
    message["From"] = adresse
    message["To"] = destinataire
    message.set_content(texte)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as serveur:
        serveur.login(adresse, mot_de_passe)
        serveur.send_message(message)


if __name__ == "__main__":
    envoyer_recap("Test : l'envoi d'e-mail du bot fonctionne.")
    print("E-mail envoyé.")