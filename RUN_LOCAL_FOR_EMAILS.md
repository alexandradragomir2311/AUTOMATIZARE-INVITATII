# 📧 Cum să primești notificări EMAIL de confirmare

## Problema:
Render.com blochează SMTP către mail.unbr.ro (toate porturile: 25, 587, 465).

## Soluția:
Rulează serverul LOCAL când vrei să testezi cu notificări email.

---

## Pași:

### 1️⃣ **Schimbă link-ul temporar la LOCAL**

În `sheets_utils.py` linia 38:
```python
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://127.0.0.1:5000/confirm')
```

### 2️⃣ **Pornește serverul local**
```bash
python confirm_server.py
```

Server va rula pe: `http://127.0.0.1:5000`

### 3️⃣ **Trimite invitație de test**
```bash
python test_send.py
```

### 4️⃣ **Click pe link din email**

Link-ul va fi: `http://127.0.0.1:5000/confirm?token=...`

### 5️⃣ **Confirmare**

- ✅ Google Sheet se actualizează
- ✅ **Email ajunge pe evenimente@unbr.ro**
- ✅ **Email salvat în folder "Confirmări Concert 2025"**

---

## ⚠️ **IMPORTANT:**

După testare, pune link-ul înapoi la Render pentru folosire reală:

În `sheets_utils.py` linia 38:
```python
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://automatizare-invitatii-1.onrender.com/confirm')
```

---

## 📊 **Pentru uz real (Concert 24 noiembrie):**

**NU ai nevoie de notificări email!**

**Google Sheet este sursa ta de adevăr:**
- Actualizat instant
- Accesibil oricând
- Linie nouă pentru Persoana 2/2
- Mai reliable decât email-ul

**Verifici Sheet-ul periodic și vezi toate confirmările! 🎉**
