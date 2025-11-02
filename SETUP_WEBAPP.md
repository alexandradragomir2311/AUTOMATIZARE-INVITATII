# 📝 Ghid de Configurare Google Apps Script Web App

Acest ghid te va ajuta să configurezi Web App-ul pentru gestionarea confirmărilor de participare cu sistem de **token-uri unice** și **termen limită 17 noiembrie 2025**.

---

## 🔐 Sistem de Securitate

### Token-uri Unice
- ✅ Fiecare invitat primește un token unic în coloana J din Sheet
- ✅ Token-ul este generat automat la prima rulare a scriptului
- ✅ Linkurile din email conțin token-ul, nu emailul
- ✅ Tokenul funcționează doar pentru destinatarul asociat
- ✅ Permite modificarea răspunsului până la termenul limită

### Termen Limită
- ⏰ **17 noiembrie 2025, ora 23:59**
- După această dată, linkurile vor afișa mesaj de expirare
- Utilizatorii pot modifica răspunsul de câte ori doresc până la termen

---

## 📋 Pași de Configurare

### 1️⃣ Creează Proiectul Google Apps Script

1. Deschide Google Sheets cu lista de invitați: 
   - [Sheet-ul INVITATII SI CONFIRMARI](https://docs.google.com/spreadsheets/d/1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg)

2. Click pe **Extensions** → **Apps Script**

3. Șterge tot codul existent din `Code.gs`

4. Copiază conținutul din fișierul `Code.gs` din proiect și lipește-l în Apps Script Editor

### 2️⃣ Configurează Script Properties (Opțional)

În Apps Script Editor:
1. Click pe ⚙️ **Project Settings**
2. Scroll la **Script Properties**
3. Click **Add script property**
4. Adaugă:
   - **Property**: `SPREADSHEET_ID`
   - **Value**: `1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg`

### 3️⃣ Publică Web App

1. În Apps Script Editor, click pe **Deploy** → **New deployment**

2. Click pe ⚙️ (roată zimțată) lângă "Select type" → Selectează **Web app**

3. Configurează deployment:
   - **Description**: `UNBR Confirmări Concert v1.0`
   - **Execute as**: **Me** (emailul tău)
   - **Who has access**: **Anyone** (Important! Trebuie să fie Anyone pentru ca invitații să poată accesa)

4. Click **Deploy**

5. **IMPORTANT**: Click pe **Authorize access**
   - Selectează contul Google
   - Click **Advanced** (dacă apare warning)
   - Click **Go to [Project name] (unsafe)**
   - Click **Allow**

6. **Copiază Web app URL** - va arăta astfel:
   ```
   https://script.google.com/macros/s/AKfycbxXXXXXXXXXXXXXXXXXXXXXX/exec
   ```

### 4️⃣ Actualizează sheets_utils.py

1. Deschide fișierul `sheets_utils.py`

2. Găsește linia:
   ```python
   WEBAPP_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
   ```

3. Înlocuiește cu URL-ul tău copiat la pasul anterior:
   ```python
   WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxXXXXXXXXXXXXXXXXXXXXXX/exec"
   ```

4. Salvează fișierul

### 5️⃣ Generează Token-uri Unice

Înainte de a trimite invitații, trebuie să generezi token-uri unice pentru toți invitații:

```bash
python generate_tokens.py
```

Acest script va:
- ✅ Crea token-uri unice pentru fiecare invitat
- ✅ Salva token-urile în coloana J din Google Sheet
- ✅ Afișa exemple de token-uri generate

**IMPORTANT**: Rulează acest script o singură dată, înainte de prima trimitere de invitații!

---

## 🧪 Testare

### Test Manual

1. Rulează scriptul de generare token-uri:
   ```bash
   python generate_tokens.py
   ```

2. Deschide Google Sheet și copiază un token din coloana J

3. Creează un URL de test:
   ```
   https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec?token=COPIED_TOKEN
   ```

4. Deschide URL-ul în browser

5. Ar trebui să vezi pagina de selecție pentru 1 sau 2 persoane

6. Selectează numărul de persoane

7. Verifică că:
   - Pagina de confirmare apare
   - Google Sheet se actualizează cu "✔ Da" în coloana H (Confirmare)
   - Numărul de persoane apare în coloana I (Răspuns)
   - Timestamp-ul apare în nota celulei din coloana J (Token)

### Test cu Email Real

1. Rulează scriptul de trimitere:
   ```bash
   python test_send.py
   ```

2. Verifică emailul primit

3. Click pe "Confirm participarea"

4. Selectează numărul de persoane

5. Verifică că Google Sheet se actualizează

### Test Expirare

Pentru a testa expirarea (în mediu de test):
1. Modifică în `Code.gs`: `const DEADLINE = new Date('2025-11-17T23:59:59');`
2. Schimbă cu o dată în trecut, ex: `const DEADLINE = new Date('2024-01-01T23:59:59');`
3. Deploy cu versiune nouă
4. Testează linkul - ar trebui să vezi mesaj de expirare
5. **NU UITA** să pui înapoi data corectă după test!

---

## 🔧 Troubleshooting

### ❌ Eroare: "Authorization required"
**Soluție**: Reautorizează scriptul:
1. Deploy → Manage deployments
2. Click pe ✏️ (Edit)
3. Click "New version"
4. Deploy și autorizează din nou

### ❌ Eroare: "Script has been disabled"
**Soluție**: 
1. Verifică că "Who has access" este setat la **Anyone**
2. Re-deploy scriptul

### ❌ Token invalid sau expirat
**Soluție**: 
1. Verifică că token-ul există în coloana J din sheet
2. Rulează din nou `python generate_tokens.py` pentru a regenera token-uri
3. Trimite din nou invitațiile

### ❌ Termenul limită a expirat
**Soluție**:
1. Dacă vrei să prelungești termenul:
   - Deschide `Code.gs` în Apps Script
   - Modifică: `const DEADLINE = new Date('2025-11-17T23:59:59');`
   - Schimbă cu noua dată
   - Deploy new version
2. Sau contactează invitații direct

### ❌ Utilizatorul nu poate modifica răspunsul
**Cauză**: Token-ul ar putea fi diferit în sheet vs email
**Soluție**:
1. Verifică că nu ai regenerat token-urile după trimiterea emailurilor
2. Dacă da, retrimite invitațiile cu noile token-uri

### ❌ Sheet-ul nu se actualizează
**Soluție**:
1. Verifică că SPREADSHEET_ID în Code.gs este corect
2. Verifică permisiunile scriptului (Execute as: Me)
3. Verifică că ai permisiuni de editare pe sheet

---

## 📊 Structura Răspunsurilor

### Coloana H - Confirmare
- `✔ Da` - Fundal verde (#d9ead3) - Participare confirmată
- `❌ Nu` - Fundal roșu (#f4cccc) - Nu poate participa

### Coloana I - Răspuns/Nr persoane
- `1 persoană` - Pentru o singură persoană
- `2 persoane` - Pentru două persoane
- `-` - Pentru refuzuri

### Coloana J - Token unic
- Token SHA-256 de 32 caractere
- Generat automat la prima rulare
- Folosit în linkurile din email
- **NU modifica manual!**
- Nota celulei conține timestamp-ul ultimei confirmări

---

## 🔒 Securitate

### Avantaje sistem token
✅ **Unic per destinatar**: Fiecare invitat are un token diferit  
✅ **Imposibil de ghicit**: Token generat cu SHA-256  
✅ **Reutilizabil**: Același invitat poate modifica răspunsul  
✅ **Termen limită**: Linkurile expiră la 17.11.2025  
✅ **Audit trail**: Timestamp în nota celulei pentru fiecare modificare  

### Ce se întâmplă dacă...
❓ **Cineva dă forward emailului?**  
→ Linkul funcționează, dar modifică răspunsul doar pentru invitatul original

❓ **Cineva încearcă să ghicească token-uri?**  
→ Token-uri de 32 caractere = practic imposibil de ghicit

❓ **După 17.11.2025?**  
→ Linkurile afișează mesaj de expirare automat

❓ **Invitatul vrea să modifice răspunsul?**  
→ Poate folosi același link din email până la termen

---

## 🔄 Actualizare Deployment

Când faci modificări în cod:

1. Apps Script Editor → **Deploy** → **Manage deployments**
2. Click pe ✏️ lângă deployment-ul activ
3. Click pe **Version** → **New version**
4. Click **Deploy**
5. **NU** este nevoie să actualizezi URL-ul în `sheets_utils.py`

---

## 📝 Notițe Importante

- ✅ Web App-ul funcționează 24/7 odată publicat
- ✅ Nu necesită server separat
- ✅ Gestionează automat autorizările
- ✅ Logs disponibile în Apps Script Editor (Executions)
- ✅ Poate fi testat direct din browser cu parametri URL

---

## 📞 Support

Pentru probleme tehnice, verifică:
1. **Execution logs**: Apps Script Editor → Executions
2. **Sheet permissions**: Verifică că scriptul are acces
3. **Email format**: Verifică că emailurile din sheet sunt corecte

---

**Versiune**: 1.0  
**Ultima actualizare**: Octombrie 2025
