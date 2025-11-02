# 📧 README Actualizat - SMTP UNBR

## ⚙️ Configurare

### 1. Google APIs (doar pentru Sheets/Drive)
   - Google Sheets API
   - Google Drive API  
   - Google Docs API
   - ❌ ~~Gmail API~~ (eliminat)

### 2. Email SMTP UNBR
   - **Server:** mail.unbr.ro
   - **Port:** 587 (STARTTLS)
   - **Account:** evenimente@unbr.ro
   - **Parola:** Configurată în `credentials/email_credentials.txt`

### 3. Configurare Rapidă

1. **Google APIs:** Folosește fișierul existent `credentials/credentials.json`
2. **Email SMTP:** Rulează `python setup_email_secure.py` pentru configurarea sigură a parolei

## 🚀 Utilizare

### Trimitere invitații (principală):
```bash
python send_invitations.py
```

### Testare SMTP:
```bash
python test_smtp.py
```

### Procesare bilete (după confirmări):
```bash
python main.py
```

## ✅ Avantaje noi:

- ✅ **Emailuri profesionale:** Expeditor `evenimente@unbr.ro`
- ✅ **Control complet:** Server UNBR, nu Gmail
- ✅ **Securitate:** Parola locală, nu OAuth complex
- ✅ **Simplitate:** Configurare mai ușoară
- ✅ **Independență:** Nu depinde de cotele Gmail API

## 📂 Fișiere noi importante:

- `smtp_utils.py` - Funcții SMTP
- `email_config.py` - Configurație email
- `test_smtp.py` - Testare conexiune
- `setup_email_secure.py` - Configurare sigură
- `SETUP_SMTP_UNBR.md` - Ghid detaliat

## 🗑️ Fișiere backup (nefolosite):

- `gmail_utils_backup.py` - Backup Gmail API (pentru istoric)