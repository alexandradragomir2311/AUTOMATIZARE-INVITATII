# 🚀 CONFIGURARE RENDER.COM - SMTP UNBR

## PASUL 1: Accesează Render Dashboard
👉 https://dashboard.render.com

Găsește serviciul **automatizare-invitatii** (sau creează unul nou dacă nu există)

---

## PASUL 2: Environment Variables (⚙️ TAB-UL "Environment")

Click pe **Environment** din meniul lateral și adaugă:

### Variables OBLIGATORII pentru SMTP UNBR:
```
SMTP_SERVER=mail.unbr.ro
SMTP_PORT=587
SMTP_USE_TLS=true
EMAIL_ADDRESS=evenimente@unbr.ro
EMAIL_PASSWORD=WsmM6$372F
```

### Variable pentru Google Sheets (PĂSTREAZĂ - folosim doar Sheets API, NU Gmail API):
```
SPREADSHEET_ID=<ID-ul tău din Google Sheet>
```

### URL-ul aplicației (nu-l mai adăuga, Render îl setează automat):
```
# Render creează automat: WEBAPP_URL=https://automatizare-invitatii.onrender.com
```

---

## PASUL 3: Verifică Fișierele pe GitHub

Asigură-te că ai toate fișierele în repository-ul conectat la Render:

### ✅ Fișiere ESENȚIALE (trebuie să existe):
- `confirm_server.py` - Server Flask pentru confirmări
- `confirmation_system.py` - Sistem SMTP pentru răspunsuri
- `email_config.py` - Configurație SMTP UNBR
- `smtp_utils.py` - Funcții SMTP
- `sheets_utils.py` - Google Sheets API
- `email_organization.py` - Organizare foldere IMAP
- `requirements.txt` - Dependențe Python
- `runtime.txt` - Versiune Python (opțional)

### ❌ ȘTERGE/IGNORĂ din repository (nu mai trebuie):
- `credentials.json` pentru Gmail API (DOAR Google Sheets API!)
- `token.pickle` pentru Gmail
- Orice referințe la Gmail API în cod

---

## PASUL 4: Verifică `requirements.txt`

Fișierul tău actual este OK ✅:
```
Flask==3.1.0
gspread==6.1.2
oauth2client==4.1.3
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
Werkzeug==3.0.1
```

**NU trebuie** biblioteci pentru Gmail API (gmail-api-python, etc.)

---

## PASUL 5: Creează/Actualizează `runtime.txt` (OPȚIONAL)

Creează fișierul `runtime.txt` în root cu:
```
python-3.11.6
```

---

## PASUL 6: PUSH pe GitHub

Dacă ai făcut modificări locale:
```bash
cd "C:\Users\40740\Desktop\AUTOMATIZARE INVITATII - Cont UNBR"
git add .
git commit -m "Configure SMTP UNBR for Render deployment"
git push origin main
```

---

## PASUL 7: Deploy pe Render

### Opțiunea A - Deploy Automat (dacă ai conectat GitHub):
1. În Render Dashboard → serviciul tău
2. Render va detecta push-ul și va face deploy automat
3. Așteaptă ~5-10 minute

### Opțiunea B - Deploy Manual:
1. În Render Dashboard → serviciul tău
2. Click **Manual Deploy** → **Deploy latest commit**
3. Așteaptă ~5-10 minute pentru build

---

## PASUL 8: Monitorizează LOGS

În Render Dashboard → **Logs** (tab din stânga):

### 🟢 Mesaje BUNE (serverul pornește OK):
```
Starting Flask server...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.x.x.x:5000
```

### 🔴 Erori POSIBILE și soluții:

**Eroare:** `ModuleNotFoundError: No module named 'gspread'`
**Soluție:** Verifică că `gspread==6.1.2` este în `requirements.txt`

**Eroare:** `SMTP Authentication Error`
**Soluție:** Verifică Environment Variables - parola trebuie să fie exact `WsmM6$372F`

**Eroare:** `Cannot find credentials.json`
**Soluție:** Trebuie să uploadezi `credentials.json` pentru Google Sheets API (NU pentru Gmail!)

---

## PASUL 9: TESTEAZĂ Deployment

### Test 1 - Verifică că serverul răspunde:
```
https://automatizare-invitatii.onrender.com/confirm?token=test
```

Ar trebui să vezi pagina cu: **"Termen limită: 10 noiembrie 2025"**

### Test 2 - Trimite o invitație de test:
```bash
python test_send.py
```

### Test 3 - Click pe linkul de confirmare din email:
- Verifică că arată deadline-ul corect: **10 noiembrie 2025**
- Confirmă participarea
- Verifică că primești email de confirmare de pe **evenimente@unbr.ro** (NU Gmail!)

---

## PASUL 10: Verifică Email-ul de Confirmare

După ce cineva confirmă, verifică:
1. ✅ Email-ul vine de pe **evenimente@unbr.ro** (NU Gmail!)
2. ✅ Email-ul se salvează în folderul **"Confirmari Concert 2025"** pe IMAP
3. ✅ Statusul se actualizează în Google Sheets

---

## ⚠️ NOTA IMPORTANTĂ despre Render FREE TIER:

**Render.com GRATUIT:**
- Serverul se oprește după **15 minute de inactivitate**
- La primul acces după oprire, durează **~30-60 secunde** să pornească
- Invitații vor vedea un mesaj "Loading..." câteva secunde

**SOLUȚIE dacă vrei să eviti oprirea:**
- Upgrade la **Render Paid Plan** ($7/lună) - serverul rulează 24/7 fără oprire
- SAU păstrează versiunea gratuită (funcționează OK, doar că are delay la primul acces)

---

## 🎯 CHECKLIST FINAL:

- [ ] Environment Variables setate pe Render (SMTP_SERVER, EMAIL_PASSWORD, etc.)
- [ ] Cod push-uit pe GitHub
- [ ] Deploy realizat pe Render (automat sau manual)
- [ ] Logs verificate - server pornit fără erori
- [ ] Test URL: `https://automatizare-invitatii.onrender.com/confirm?token=test`
- [ ] Test invitație trimisă și link funcționează
- [ ] Email confirmare vine de pe **evenimente@unbr.ro** ✅

---

## 📞 DACĂ APAR PROBLEME:

1. **Verifică LOGS** pe Render Dashboard
2. **Verifică Environment Variables** - parola corectă?
3. **Verifică că fișierele sunt push-uite** pe GitHub
4. **Așteaptă 5-10 minute** după deploy pentru ca modificările să se propage

---

**URL FINAL PENTRU INVITAȚII:**
```
https://automatizare-invitatii.onrender.com/confirm
```

Acest URL va fi generat automat în `sheets_utils.py` pentru fiecare invitație! ✅
