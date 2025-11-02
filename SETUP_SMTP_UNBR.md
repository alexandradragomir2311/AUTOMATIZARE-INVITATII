# Configurare Email SMTP UNBR

Acest ghid explică cum să configurezi proiectul pentru a trimite emailuri prin serverul SMTP personalizat al UNBR (`evenimente@unbr.ro`) în loc de Gmail API.

## Modificări efectuate

### 1. Fișiere noi create:
- `email_config.py` - Configurația pentru serverul SMTP UNBR
- `smtp_utils.py` - Funcții pentru trimiterea emailurilor prin SMTP
- `test_smtp.py` - Script de testare pentru configurația SMTP

### 2. Fișiere modificate:
- `send_invitations.py` - Actualizat să folosească noul sistem SMTP

## Configurația serverului SMTP

Următoarele setări sunt configurate automat:

### SMTP (Trimitere emailuri)
- **Server:** mail.unbr.ro
- **Port:** 587 (cu STARTTLS)
- **Criptare:** SSL/TLS
- **Adresa:** evenimente@unbr.ro

### IMAP (Primire emailuri) - opțional
- **Server:** mail.unbr.ro  
- **Port:** 993
- **Criptare:** SSL/TLS

### POP3 (Primire emailuri) - opțional
- **Server:** mail.unbr.ro
- **Port:** 995
- **Criptare:** SSL/TLS

## Configurarea parolei

Există 3 modalități de a seta parola pentru `evenimente@unbr.ro`:

### Opțiunea 1: Fișier de credentiale (Recomandat)
```bash
# Creează directorul credentials dacă nu există
mkdir credentials

# Creează fișierul cu parola
echo "parola_ta_aici" > credentials/email_credentials.txt
```

### Opțiunea 2: Variabilă de mediu
```powershell
# Windows PowerShell
$env:EMAIL_PASSWORD = "parola_ta_aici"
```

### Opțiunea 3: Introducere manuală
Dacă nu există parola în fișier sau variabilă de mediu, scriptul va cere introducerea manuală.

## Testarea configurației

### 1. Testează conexiunea SMTP:
```bash
python test_smtp.py
```

Acest script va:
- Verifica conexiunea la serverul SMTP
- Trimite un email de test către adresa specificată
- Confirma că totul funcționează corect

### 2. Testează trimiterea invitațiilor:
```bash
python send_invitations.py
```

## Avantajele noului sistem

1. **Control complet** - Folosești propriul server de email UNBR
2. **Branding profesional** - Emailurile vin de la `evenimente@unbr.ro`
3. **Securitate** - Nu mai depinzi de Gmail API și OAuth
4. **Simplitate** - Configurare mai simplă, fără autentificare OAuth complexă
5. **Flexibilitate** - Poți trimite emailuri de pe orice server ce suportă SMTP

## Rezolvarea problemelor

### Eroare de autentificare:
- Verifică că parola este corectă
- Asigură-te că autentificarea externă este activată pe contul `evenimente@unbr.ro`
- Verifică că nu există restricții IP pe serverul UNBR

### Probleme de conexiune:
- Verifică că portul 587 nu este blocat de firewall
- Încearcă portul 465 în loc de 587 (modifică în `email_config.py`)
- Verifică conexiunea la internet

### Emailuri în SPAM:
- Configurează SPF, DKIM și DMARC pentru domeniul unbr.ro
- Contactează administratorul serverului pentru optimizări

## Revenirea la Gmail (dacă este necesar)

Pentru a reveni la sistemul Gmail, modifică `send_invitations.py`:
```python
# Înlocuiește
from smtp_utils import send_invitation_with_ticket

# Cu
from gmail_utils import send_invitation_with_ticket
```

## Securitate

- **NU** pune parola direct în cod
- Folosește fișierul `credentials/email_credentials.txt` (este în .gitignore)
- Păstrează parola în siguranță
- Schimbă parola regulat conform politicilor UNBR