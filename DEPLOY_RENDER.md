# 🚀 Ghid Deployment Server Flask pe Render.com

## ✅ DE CE RENDER.COM?
- **GRATUIT permanent** - serverul rulează 24/7
- Linkurile din invitații vor funcționa **MEREU**, chiar dacă închizi laptopul
- Google Sheets se actualizează automat la fiecare confirmare
- Foarte ușor de configurat (10 minute)

---

## 📝 PAȘI PENTRU DEPLOYMENT

### 1️⃣ Creează cont pe Render.com (GRATUIT)

1. Mergi pe **https://render.com**
2. Click pe **"Get Started for Free"**
3. Înregistrează-te cu **GitHub** (recomandat) sau email

---

### 2️⃣ Creează un repository pe GitHub

**Opțiunea A - Cu GitHub Desktop (mai ușor):**

1. Descarcă GitHub Desktop: https://desktop.github.com
2. Instalează și conectează-te cu contul tău GitHub
3. Click pe **"File" → "Add Local Repository"**
4. Selectează folderul: `C:\Users\40740\Desktop\AUTOMATIZARE INVITATII`
5. Click pe **"Create Repository"** apoi **"Publish repository"**
6. Denumire: `unbr-confirmari` (sau alt nume)
7. **IMPORTANT:** Bifează **"Keep this code private"** (pentru securitate)
8. Click **"Publish repository"**

**Opțiunea B - Manual din terminal:**

```powershell
cd "C:\Users\40740\Desktop\AUTOMATIZARE INVITATII"

# Inițializează Git
git init

# Adaugă toate fișierele (EXCEPȚIE: credentials vor fi adăugate separat pe Render)
git add confirm_server.py requirements.txt runtime.txt sheets_utils.py gmail_utils.py docs_utils.py

# Commit
git commit -m "Initial deployment"

# Conectează la GitHub (înlocuiește USERNAME cu contul tău)
git remote add origin https://github.com/USERNAME/unbr-confirmari.git

# Push
git branch -M main
git push -u origin main
```

---

### 3️⃣ Deploy pe Render.com

1. **Loghează-te pe Render.com**
2. Click pe **"New +"** → **"Web Service"**
3. Selectează **"Connect a repository"** → alege `unbr-confirmari`
4. **Configurare:**
   - **Name:** `unbr-confirmari`
   - **Region:** Europe (Frankfurt) - cel mai apropiat de România
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python confirm_server.py`
   - **Instance Type:** `Free`

5. Click pe **"Advanced"** → **"Add Environment Variable"**
6. **NU trebuie să adaugi variabile** - credențialele se urcă manual (vezi pasul următor)

7. Click **"Create Web Service"**

---

### 4️⃣ Urcă fișierul credentials.json pe Render

**IMPORTANT:** Nu putem pune `credentials.json` pe GitHub (securitate!)

**Metoda 1 - Shell Render (RECOMANDAT):**

1. După ce serviciul s-a creat, mergi la tab-ul **"Shell"**
2. Click pe **"Launch Shell"**
3. În consolă, rulează:
   ```bash
   mkdir -p credentials
   cat > credentials/credentials.json
   ```
4. Copiază **ÎNTREG conținutul** din `credentials/credentials.json` de pe laptopul tău
5. Lipește în shell
6. Apasă **Ctrl+D** de 2 ori pentru a salva
7. Verifică:
   ```bash
   cat credentials/credentials.json
   ```

**Metoda 2 - Environment Variables (alternativă):**

1. În Render Dashboard → **"Environment"** → **"Add Secret File"**
2. **Filename:** `credentials/credentials.json`
3. Copiază conținutul fișierului `credentials.json`
4. Click **"Save Changes"**

---

### 5️⃣ Actualizează WEBAPP_URL în sheets_utils.py

1. **După deployment, Render îți va da un URL** de forma:
   ```
   https://unbr-confirmari.onrender.com
   ```

2. **Deschide `sheets_utils.py`** și modifică:
   ```python
   # ÎNAINTE (localhost - PENTRU TESTE LOCALE)
   WEBAPP_URL = 'http://localhost:5000/confirm'
   
   # DUPĂ (Render - PENTRU PRODUCȚIE)
   WEBAPP_URL = 'https://unbr-confirmari.onrender.com/confirm'
   ```

3. **Salvează și face push pe GitHub:**
   ```powershell
   git add sheets_utils.py
   git commit -m "Update WEBAPP_URL to production"
   git push
   ```

4. **Render va redeploya automat** în 1-2 minute

---

### 6️⃣ Testează sistemul

1. **Trimite un email de test:**
   ```powershell
   .venv\Scripts\python.exe test_send.py
   ```

2. **Verifică email-ul** la alexandradragomir23@yahoo.com

3. **Click pe linkul de confirmare** - ar trebui să se deschidă pe `https://unbr-confirmari.onrender.com`

4. **Alege numărul de persoane** și verifică:
   - ✅ Pagina de confirmare se afișează corect
   - ✅ **Google Sheets se actualizează** cu răspunsul
   - ✅ Primești **email de confirmare**

---

## 🔧 VERIFICĂRI IMPORTANTE

### ✅ Serverul rulează permanent?
- Mergi pe Render Dashboard → serviciul tău
- Status ar trebui să fie **"Live"** (verde)
- Dacă este "Sleeping", click pe **"Resume"**

### ✅ Google Sheets se actualizează?
- După ce cineva confirmă, verifică sheet-ul
- Coloana H (Confirmare) ar trebui să aibă: `✔ Da - 1 persoană` sau `✔ Da - Persoana 1/2`
- Coloana I (Răspuns) ar trebui să fie: `1 persoană` sau `2 persoane`
- **Dacă se creează 2 rânduri pentru 2 persoane** → ✅ PERFECT!
- **Dacă se șterge rândul 2 când schimbi la 1 persoană** → ✅ PERFECT!

### ✅ Logs pentru debugging
1. În Render Dashboard → **"Logs"** tab
2. Vezi toate request-urile și eventualele erori
3. Dacă ceva nu merge, verifică aici!

---

## 🚨 TROUBLESHOOTING

### Problema: "Application failed to respond"
**Soluție:** Verifică în Logs că Flask pornește corect:
```
🚀 SERVER PORNIT pe http://0.0.0.0:5000
* Serving Flask app 'confirm_server'
```

### Problema: Google Sheets nu se actualizează
**Soluție:** Verifică că `credentials.json` a fost încărcat corect pe Render:
```bash
ls -la credentials/
cat credentials/credentials.json
```

### Problema: Email-urile nu se trimit
**Soluție:** Verifică că Gmail API este activat și că `token.pickle` există.
- Dacă `token.pickle` lipsește pe Render, va trebui reautentificat
- Rulează local `test_send.py` pentru a regenera `token.pickle`
- Apoi urcă-l pe Render la fel ca `credentials.json`

---

## 📊 MONITORIZARE

### Render Dashboard
- **Metrics:** Vezi traficul, CPU, memorie
- **Logs:** Vezi toate request-urile de confirmare
- **Events:** Vezi când se face deploy

### Google Sheets
- **Coloana H:** Status confirmare (verde = Da, roșu = Nu)
- **Coloana I:** Număr persoane (1 persoană, 2 persoane, Persoana 2)
- **Notițe pe coloana J (Token):** Data confirmării

---

## ✨ AVANTAJE DUPĂ DEPLOYMENT

✅ **Linkurile funcționează PERMANENT** (chiar dacă închizi laptopul)
✅ **Google Sheets se actualizează AUTOMAT** la fiecare confirmare
✅ **Zero costuri** - Render.com Free tier
✅ **SSL inclus** - linkurile sunt https:// (securizate)
✅ **Monitoring inclus** - vezi toate confirmările în Logs
✅ **Auto-deployment** - când faci push pe GitHub, se actualizează automat

---

## 🎯 FOLOSIRE DUPĂ DEPLOYMENT

### Pentru a trimite invitații:
```powershell
.venv\Scripts\python.exe test_send.py
```

### Pentru a verifica confirmări:
- Deschide Google Sheets
- Verifică coloanele H și I
- Filtrează după "✔ Da" pentru a vedea cine participă

### Pentru a vedea logs:
- Mergi pe Render Dashboard → serviciul tău → tab "Logs"
- Vezi fiecare click pe link și fiecare confirmare

---

## 📞 SUPORT

Dacă întâmpini probleme:
1. Verifică **Logs** pe Render.com
2. Verifică că `credentials.json` există pe server
3. Testează linkul manual: `https://unbr-confirmari.onrender.com/confirm?token=TEST`
4. Contactează-mă pentru asistență

---

**🎉 SUCCES CU DEPLOYMENT-UL!**
