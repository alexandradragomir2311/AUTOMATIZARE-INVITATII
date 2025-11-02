# 🚀 CONECTARE RENDER CU GITHUB - PAS CU PAS

## ✅ CE AI DEJA FĂCUT:
- ✅ Cod pe GitHub: https://github.com/alexandradragomir2311/AUTOMATIZARE-INVITATII
- ✅ Toate fișierele necesare sunt push-uite

---

## 📋 ACUM URMEAZĂ (5 MINUTE):

### PASUL 1: Deschide Render
👉 Click aici: **https://dashboard.render.com/**

- Dacă nu ai cont, click **Get Started** și creează cont cu GitHub
- Dacă ai cont, login

---

### PASUL 2: Creează Web Service Nou
1. Click butonul mare albastru **"New +"** (sus dreapta)
2. Din meniu, selectează **"Web Service"**

---

### PASUL 3: Conectează GitHub
Se deschide pagina "Create a new Web Service"

**Dacă NU vezi repository-ul tău:**
1. Click pe **"Connect account"** sau **"Configure account"**
2. Va apărea popup GitHub
3. Click **"Authorize Render"**
4. Selectează **"All repositories"** SAU doar `AUTOMATIZARE-INVITATII`
5. Click **"Install"**

**Dacă VEZI repository-ul:**
1. Găsește în listă: `alexandradragomir2311/AUTOMATIZARE-INVITATII`
2. Click pe butonul **"Connect"** de lângă el

---

### PASUL 4: Configurează Serviciul
Vei vedea un formular. Completează ASA:

#### 📝 Secțiunea "Settings":
```
Name: automatizare-invitatii-unbr
Region: Frankfurt (EU Central)
Branch: main
Root Directory: (lasă gol)
Runtime: Python 3
```

#### 📝 Secțiunea "Build & Deploy":
```
Build Command: pip install -r requirements.txt
Start Command: python confirm_server.py
```

#### 📝 Secțiunea "Plan":
```
Instance Type: Free (0$/month)
```

---

### PASUL 5: Adaugă Environment Variables
Scroll jos până vezi secțiunea **"Environment Variables"**

Click **"Add Environment Variable"** și adaugă EXACT acestea (5 variabile):

**Variabila 1:**
```
Key: SMTP_SERVER
Value: mail.unbr.ro
```

**Variabila 2:**
```
Key: SMTP_PORT
Value: 587
```

**Variabila 3:**
```
Key: SMTP_USE_TLS
Value: true
```

**Variabila 4:**
```
Key: EMAIL_ADDRESS
Value: evenimente@unbr.ro
```

**Variabila 5:**
```
Key: EMAIL_PASSWORD
Value: WsmM6$372F
```

---

### PASUL 6: Creează Serviciul
1. Scroll până jos de tot
2. Click butonul mare albastru **"Create Web Service"**
3. **AȘTEAPTĂ 5-10 MINUTE** - Render construiește aplicația

Vei vedea:
- Mai întâi: "Build in progress..." (2-3 min)
- Apoi: "Deploy in progress..." (1-2 min)
- Final: "Live" cu un cerc verde ✅

---

### PASUL 7: Copiază URL-ul
După ce deploy-ul e gata:

1. Sus în pagină vei vedea URL-ul tău, ceva de genul:
   ```
   https://automatizare-invitatii-unbr.onrender.com
   ```

2. **COPIAZĂ URL-UL** (click pe el să-l selectezi, apoi Ctrl+C)

3. **SPUNE-MI URL-UL** și actualizez automat `sheets_utils.py`!

---

## 🔍 VERIFICARE DEPLOY:

### Test 1 - Verifică Logs:
1. În pagina serviciului Render, click pe **"Logs"** (meniu stânga)
2. Trebuie să vezi:
   ```
   🚀 SERVER PORNIT pe http://localhost:5000
   * Running on all addresses (0.0.0.0)
   * Running on http://0.0.0.0:10000
   ```

### Test 2 - Testează URL-ul:
Deschide în browser (înlocuiește cu URL-ul tău):
```
https://automatizare-invitatii-unbr.onrender.com/confirm?token=test
```

Trebuie să vezi pagina cu: **"Termen limită: 10 noiembrie 2025"**

---

## ❌ DACĂ APARE EROARE:

### Eroare: "Build failed"
**Soluție**: Click pe **"Logs"**, caută eroarea și spune-mi ce scrie

### Eroare: "Deploy failed"  
**Soluție**: Verifică că ai adăugat TOATE cele 5 Environment Variables

### Eroare: "Application failed to respond"
**Soluție**: Verifică că Start Command e exact: `python confirm_server.py`

---

## 📞 SPUNE-MI:
1. ✅ La ce pas ai ajuns?
2. ✅ Ce URL ți-a dat Render?
3. ❌ Dacă e vreo eroare, ce scrie în Logs?

**ȘI ACTUALIZEZ EU AUTOMAT `sheets_utils.py` CU URL-UL CORECT!** 🚀
