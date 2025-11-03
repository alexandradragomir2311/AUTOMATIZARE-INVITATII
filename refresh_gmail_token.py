"""
Script pentru a regenera token-ul cu Gmail scope inclus
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def main():
    print("🔄 Regenerare token cu Gmail scope...")
    
    creds = None
    token_file = 'credentials/token.pickle'
    
    # Dacă există token vechi, încercă să-l refreshăm
    if os.path.exists(token_file):
        print("⚠️ Token vechi găsit, îl ștergem...")
        os.remove(token_file)
    
    # Flow de autentificare
    print("🌐 Deschid browser pentru autentificare...")
    print("⚠️ IMPORTANT: Acceptă toate permisiunile (Sheets, Drive, Gmail)!")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/credentials.json', 
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    
    # Salvează token-ul
    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)
    
    print("✅ Token generat cu succes cu Gmail scope!")
    print(f"✅ Scopes incluse: {creds.scopes}")
    
    # Generează base64 pentru Render
    import base64
    token_json = creds.to_json()
    token_base64 = base64.b64encode(token_json.encode()).decode()
    
    print("\n" + "="*80)
    print("📋 Token pentru Render (GOOGLE_TOKEN):")
    print("="*80)
    print(token_base64[:100] + "..." + f" ({len(token_base64)} caractere)")
    print("\n⚠️ Copiază acest token și actualizează GOOGLE_TOKEN în Render!")
    
    # Salvează într-un fișier
    with open('token_base64_gmail.txt', 'w') as f:
        f.write(token_base64)
    print("✅ Token salvat și în fișierul token_base64_gmail.txt")

if __name__ == '__main__':
    main()
