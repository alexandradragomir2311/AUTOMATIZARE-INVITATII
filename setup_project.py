import os
import json

# Definirea directorului rădăcină
ROOT_DIR = r"C:\Users\40740\Desktop\AUTOMATIZARE INVITATII"

# Structura folderelor
FOLDERS = [
    'templates',
    'credentials',
    'static'
]

# Conținutul fișierelor
FILES = {
    'main.py': '''"""
Main entry point for invitation automation.
Reads data from Google Sheets, generates emails using Docs template,
sends via Gmail API, and updates the sheet.
"""

from gmail_utils import send_invitation_email
from sheets_utils import get_guest_list, update_guest_status
from docs_utils import generate_invitation_text

def main() -> None:
    """
    Main workflow for sending invitations.
    """
    guests = get_guest_list()
    for guest in guests:
        invitation_text = generate_invitation_text(guest)
        if send_invitation_email(guest['email'], "Invitație", invitation_text):
            update_guest_status(guest['id'], True, "Trimis")

if __name__ == "__main__":
    main()
''',

    'gmail_utils.py': '''"""
Gmail utility functions for sending emails via Gmail API.
"""
from typing import Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def send_invitation_email(recipient: str, subject: str, html_content: str) -> bool:
    """
    Sends an invitation email to the recipient.
    """
    try:
        # Gmail API implementation here
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
''',

    'sheets_utils.py': '''"""
Google Sheets utility functions for reading and updating guest data.
"""
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_guest_list() -> List[Dict[str, str]]:
    """
    Reads guest data from Google Sheets.
    """
    return []

def update_guest_status(guest_id: str, mail_sent: bool, confirmation: str) -> None:
    """
    Updates the guest row with mail sent status and confirmation.
    """
    pass
''',

    'docs_utils.py': '''"""
Google Docs utility functions for generating personalized invitation text.
"""
from typing import Dict

def generate_invitation_text(guest_data: Dict[str, str]) -> str:
    """
    Generates personalized invitation text using Google Docs template.
    """
    return ""
''',

    'flask_server.py': '''"""
Flask server for handling confirmation links and guest responses.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/confirm", methods=["GET"])
def confirm():
    """
    Endpoint for guest confirmation.
    """
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
''',

    'templates/email_template.html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invitație</title>
</head>
<body>
    <p>Dragă {{Nume}} {{Prenume}},</p>
    <p>{{InvitatieText}}</p>
    <br>
    <footer>
        <img src="cid:logo" alt="Logo" width="120" /><br>
        <small>Vă așteptăm cu drag!</small>
    </footer>
</body>
</html>
''',

    'credentials/credentials.json': json.dumps({
        "PLACEHOLDER": "Adaugă aici fișierul credentials.json descărcat din Google Cloud Console."
    }, indent=4),

    'README.md': '''# Automatizare Invitații

Automatizare completă pentru trimiterea invitațiilor personalizate pe email.

## Instalare

1. Instalează dependențele:
```
pip install google-auth google-auth-oauthlib google-api-python-client flask
```

2. Adaugă credentials.json în folderul credentials/
3. Pornește serverul Flask: `python flask_server.py`
4. Rulează: `python main.py`
'''
}

def create_project_structure():
    """Creează structura proiectului."""
    # Creare foldere
    for folder in FOLDERS:
        folder_path = os.path.join(ROOT_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Creat folder: {folder_path}")

    # Creare fișiere
    for file_path, content in FILES.items():
        full_path = os.path.join(ROOT_DIR, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Creat fișier: {full_path}")

if __name__ == "__main__":
    create_project_structure()