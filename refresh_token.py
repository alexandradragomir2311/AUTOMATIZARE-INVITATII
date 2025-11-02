"""
Generează un token fresh pentru Render
"""
from sheets_utils import get_credentials
import pickle
import base64

print("🔄 Generăm token fresh...")

# Forțează refresh
creds = get_credentials()

# Salvează token-ul fresh
with open('credentials/token.pickle', 'wb') as token:
    pickle.dump(creds, token)

# Convertește în base64
with open('credentials/token.pickle', 'rb') as f:
    token_bytes = f.read()

token_b64 = base64.b64encode(token_bytes).decode('utf-8')

# Salvează pentru Render
with open('render_token_fresh.txt', 'w') as f:
    f.write(token_b64)

print(f"\n✅ Token fresh generat!")
print(f"📄 Salvat în: render_token_fresh.txt ({len(token_b64)} caractere)")
print(f"\n🔧 ACTUALIZEAZĂ pe Render:")
print(f"   Key: GOOGLE_TOKEN")
print(f"   Value: (copiază din render_token_fresh.txt)")
