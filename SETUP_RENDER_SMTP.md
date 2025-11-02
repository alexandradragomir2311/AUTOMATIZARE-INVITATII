# 🚀 CONFIGURARE RENDER.COM CU SMTP UNBR

## PROBLEMA
Render.com folosește încă Gmail API vechi. Trebuie să configurăm să folosească SMTP UNBR (evenimente@unbr.ro).

## SOLUȚIA - Actualizează Environment Variables pe Render

### Pasul 1: Accesează Render Dashboard
1. Mergi la: https://dashboard.render.com
2. Găsește serviciul: **automatizare-invitatii**
3. Click pe serviciul tău

### Pasul 2: Actualizează Environment Variables
Click pe **Environment** din meniul stânga și adaugă/actualizează:

```
SMTP_SERVER=mail.unbr.ro
SMTP_PORT=587
SMTP_USE_TLS=true
EMAIL_ADDRESS=evenimente@unbr.ro
EMAIL_PASSWORD=WsmM6$372F
WEBAPP_URL=https://automatizare-invitatii.onrender.com/confirm
```

### Pasul 3: Verifică Fișierele pe Render
Asigură-te că ai următoarele fișiere în repository-ul de pe Render:

#### `confirm_server.py` - TREBUIE să folosească SMTP, nu Gmail!
```python
from confirmation_system import send_confirmation_response

# În funcția confirm():
send_confirmation_response(nume, email, "confirmare")  # NU MailApp sau Gmail API!
```

#### `confirmation_system.py` - Folosește SMTP UNBR
```python
from smtp_utils import get_email_config
import smtplib

def send_confirmation_response(guest_name, guest_email, response_type):
    config = get_email_config()
    # Trimite prin SMTP
    with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
        server.starttls()
        server.login(config.email_address, config.email_password)
        server.send_message(message)
```

#### `email_config.py` - Configurația SMTP
```python
@dataclass
class EmailConfig:
    smtp_server: str = "mail.unbr.ro"
    smtp_port: int = 587
    email_address: str = "evenimente@unbr.ro"
    email_password: str = ""
    
    @classmethod
    def load_from_env(cls):
        config = cls()
        config.email_password = os.getenv('EMAIL_PASSWORD', '')
        config.smtp_server = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
        config.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        config.email_address = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
        return config
```

### Pasul 4: Actualizează `requirements.txt` pe Render
```
Flask==3.0.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
gspread==5.12.0
python-dotenv==1.0.0
# NU mai trebuie: gmail-api-python sau alte biblioteci Gmail
```

### Pasul 5: Push modificările pe GitHub
```bash
git add .
git commit -m "Switch to SMTP UNBR for confirmations"
git push origin main
```

### Pasul 6: Redeploy pe Render
1. În Render Dashboard → serviciul tău
2. Click **Manual Deploy** → **Deploy latest commit**
3. Așteaptă ~5-10 minute pentru build

### Pasul 7: Verifică Logs
1. În Render Dashboard → **Logs**
2. Caută erori la pornire
3. Verifică că folosește SMTP: "Email trimis... prin SMTP mail.unbr.ro"

### Pasul 8: Testează
1. Trimite o invitație nouă (cu linkul Render)
2. Click pe link de confirmare
3. Verifică că arată: **"Termen limită: 10 noiembrie 2025"**
4. Confirmă → Verifică că emailul vine de pe **evenimente@unbr.ro**

## FIȘIERE IMPORTANTE DE VERIFICAT PE RENDER

### ❌ ȘTERGE SAU COMENTEAZĂ - Nu mai trebuie Gmail:
- Nu trebuie `credentials.json` sau `token.pickle` pentru Gmail API
- Nu trebuie import-uri `from googleapiclient.discovery import build` pentru Gmail
- Nu trebuie `MailApp.sendEmail()` (asta e doar în Google Apps Script)

### ✅ TREBUIE SĂ EXISTE:
- `email_config.py` - configurație SMTP
- `smtp_utils.py` - funcții SMTP
- `confirmation_system.py` - sistem confirmări SMTP
- `confirm_server.py` - server Flask cu SMTP
- `email_organization.py` - organizare foldere IMAP

## DEADLINE ACTUALIZAT
Toate fișierele trebuie să aibă:
```python
DEADLINE = datetime(2025, 11, 10, 23, 59, 59)  # 10 NOIEMBRIE!
```

## VERIFICARE FINALĂ
După deploy, accesează:
```
https://automatizare-invitatii.onrender.com/confirm?token=test
```

Ar trebui să vezi pagina cu: **"Termen limită: 10 noiembrie 2025"**

---

**Notă**: Render.com este gratuit dar serverul se oprește după 15 minute de inactivitate. Se reactivează automat când cineva accesează linkul (poate dura ~30 secunde).
