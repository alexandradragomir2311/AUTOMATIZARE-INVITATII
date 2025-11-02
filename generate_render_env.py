"""
Script pentru a genera environment variables pentru Render.com
Rulează acest script local și copiază output-ul în Render Environment Variables
"""
import pickle
import json
import base64
import os

# Paths
TOKEN_PATH = 'credentials/token.pickle'
CREDENTIALS_PATH = 'credentials/credentials.json'

print("=" * 60)
print("GENERARE ENVIRONMENT VARIABLES PENTRU RENDER.COM")
print("=" * 60)

# 1. Citește token.pickle
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, 'rb') as f:
        token_bytes = f.read()
    
    token_b64 = base64.b64encode(token_bytes).decode('utf-8')
    print("\n✅ GOOGLE_TOKEN generat cu succes!")
    print("\nAdaugă această variabilă pe Render:")
    print("-" * 60)
    print("Key: GOOGLE_TOKEN")
    print(f"Value: {token_b64[:50]}... (total {len(token_b64)} caractere)")
    print("-" * 60)
    
    # Salvează într-un fișier pentru copy-paste
    with open('render_token.txt', 'w') as f:
        f.write(token_b64)
    print("\n📄 Token salvat în: render_token.txt")
else:
    print(f"\n❌ EROARE: Fișierul {TOKEN_PATH} nu există!")
    print("Rulează mai întâi test_send.py pentru a genera token.pickle")

# 2. Verifică credentials.json
if os.path.exists(CREDENTIALS_PATH):
    with open(CREDENTIALS_PATH, 'r') as f:
        creds_content = f.read()
    
    # Verifică dacă e placeholder
    if "PLACEHOLDER" in creds_content:
        print(f"\n⚠️  WARNING: {CREDENTIALS_PATH} conține doar placeholder!")
        print("Dacă aplicația funcționează local, atunci GOOGLE_TOKEN este suficient.")
    else:
        print("\n✅ GOOGLE_CREDENTIALS găsit!")
        print("\nAdaugă această variabilă pe Render:")
        print("-" * 60)
        print("Key: GOOGLE_CREDENTIALS")
        print(f"Value: (conținutul din credentials.json)")
        print("-" * 60)
else:
    print(f"\n⚠️  Fișierul {CREDENTIALS_PATH} nu există")

print("\n" + "=" * 60)
print("PAȘI URMĂTORI:")
print("=" * 60)
print("1. Mergi la: https://dashboard.render.com/web/automatizare-invitatii")
print("2. Click pe 'Environment' (meniu stânga)")
print("3. Click 'Add Environment Variable' sau 'Edit Environment'")
print("4. Adaugă:")
print("   - Key: GOOGLE_TOKEN")
print("   - Value: (copiază din render_token.txt)")
print("5. Click 'Save Changes'")
print("6. Așteaptă redeploy (~2-3 minute)")
print("=" * 60)
