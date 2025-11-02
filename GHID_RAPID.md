# 🎯 Ghid Rapid - Sistem Complet de Invitații cu Token-uri Unice

## ✅ Ce am implementat

### 1. **Sistem de Token-uri Unice**
- Fiecare invitat primește un token unic SHA-256 (32 caractere)
- Token-ul este salvat în coloana J din Google Sheet
- Linkurile din email folosesc token-ul, nu emailul
- **Securitate**: Imposibil de ghicit, unic per destinatar

### 2. **Termen Limită**
- **17 noiembrie 2025, ora 23:59**
- După această dată, linkurile afișează mesaj de expirare
- Invitații pot modifica răspunsul de câte ori doresc până la termen

### 3. **Pagină Interactivă de Confirmare**
- Selecție: 1 persoană sau 2 persoane
- Design modern și responsive
- Mesaje personalizate pentru fiecare răspuns
- Notificare dacă utilizatorul modifică un răspuns anterior

### 4. **Actualizare Automată Google Sheet**
- Coloana H: `✔ Da` (verde) sau `❌ Nu` (roșu)
- Coloana I: Număr persoane (`1 persoană`, `2 persoane`, `-`)
- Coloana J: Token unic + timestamp în notă

---

## 🚀 Pași de Utilizare (Ordonați)

### Pasul 1: Configurare Google Apps Script (O singură dată)

1. **Deschide Google Sheet**:
   - [Sheet INVITATII SI CONFIRMARI](https://docs.google.com/spreadsheets/d/1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg)

2. **Creează Apps Script**:
   - Extensions → Apps Script
   - Șterge tot codul existent
   - Copiază conținutul din `Code.gs`
   - Salvează (Ctrl+S)

3. **Publică Web App**:
   - Deploy → New deployment
   - Type: Web app
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Deploy → Authorize access
   - Copiază Web app URL

4. **Actualizează sheets_utils.py**:
   ```python
   WEBAPP_URL = "URL_COPIAT_DE_MAI_SUS"
   ```

### Pasul 2: Generare Token-uri (O singură dată înainte de prima trimitere)

```bash
python generate_tokens.py
```

**Ce face**:
- ✅ Generează token-uri unice pentru toți invitații
- ✅ Salvează în coloana J din Google Sheet
- ✅ Afișează exemple de token-uri

**IMPORTANT**: 
- Rulează DOAR ÎNAINTE de prima trimitere de invitații
- NU rula din nou după ce ai trimis emailuri (token-urile se vor schimba!)

### Pasul 3: Trimitere Invitații

**Pentru testare** (trimite doar către tine):
```bash
python test_send.py
```

**Pentru trimitere completă** (trimite către toți invitații):
```bash
python main.py
```

sau

```bash
python send_invitations.py
```

---

## 📧 Cum Funcționează Emailul

### Linkuri în Email

#### Butonul "Confirm participarea":
```
https://script.google.com/.../exec?token=TOKEN_UNIC&resp=da
```

#### Butonul "Nu pot participa":
```
https://script.google.com/.../exec?token=TOKEN_UNIC&resp=nu
```

### Flow Utilizator

1. **Invitatul primește emailul** cu 2 butoane
2. **Click pe "Confirm participarea"**:
   - Se deschide pagina: "Pentru câte persoane?"
   - Selectează "1 persoană" sau "2 persoane"
   - Vede mesaj de confirmare
   - Google Sheet se actualizează automat
3. **Poate modifica răspunsul**:
   - Folosește același link din email
   - Vede notificare că răspunsul va fi actualizat
   - Alege din nou

---

## 🔍 Verificări și Monitorizare

### Verifică Status în Google Sheet

| Coloană | Semnificație | Culoare |
|---------|-------------|---------|
| G (Email trimis) | `Trimis ✅` / `Email invalid ❌` / `Lipsă email ⚠️` | Verde / Roșu / Galben |
| H (Confirmare) | `✔ Da` / `❌ Nu` | Verde deschis / Roșu deschis |
| I (Răspuns) | `1 persoană` / `2 persoane` / `-` | - |
| J (Token) | Token unic (32 caractere) | Notă = timestamp |

### Monitorizare în Apps Script

1. Apps Script Editor → **Executions**
2. Vezi toate cererile procesate
3. Verifică erori (dacă există)

---

## 🛠️ Troubleshooting

### ❌ "Token invalid sau expirat"
**Cauză**: Token-ul nu există în coloana J  
**Soluție**: Rulează `python generate_tokens.py`

### ❌ "Termenul limită a expirat"
**Cauză**: Data curentă > 17.11.2025  
**Soluție**: 
1. Modifică în `Code.gs`: `const DEADLINE = new Date('NOUA_DATA');`
2. Deploy new version

### ❌ "Authorization required"
**Soluție**: 
1. Apps Script → Deploy → Manage deployments
2. Edit → New version → Deploy
3. Reautorizează

### ❌ Invitatul nu poate modifica răspunsul
**Cauză**: Token-uri regenerate după trimiterea emailurilor  
**Soluție**: 
1. NU rula din nou `generate_tokens.py`
2. Dacă ai rulat, retrimite invitațiile

---

## 📊 Raportare

### Câte persoane au confirmat?

```
=COUNTIF(H:H,"✔ Da")
```

### Câți invitați în total?

```
=COUNTA(H2:H) - COUNTIF(G:G,"Email invalid ❌") - COUNTIF(G:G,"Lipsă email ⚠️")
```

### Total persoane confirmate?

```
=SUMIF(I:I,"1 persoană",1) + SUMIF(I:I,"2 persoane",2)
```

---

## 🔒 Securitate - De ce este sigur?

✅ **Token-uri unice**: Fiecare invitat = token diferit  
✅ **SHA-256**: Imposibil de ghicit (2^256 combinații)  
✅ **Acces Anyone**: Da, dar fără token valid nu se modifică nimic  
✅ **Modificări permise**: Utilizatorul poate schimba răspunsul  
✅ **Termen limită**: Auto-expirare la 17.11.2025  
✅ **Audit**: Timestamp în nota fiecărui token  

---

## 📝 Checklist Final

Înainte de trimiterea invitațiilor:

- [ ] Am configurat Google Apps Script
- [ ] Am publicat Web App (Who has access = Anyone)
- [ ] Am copiat Web app URL în `sheets_utils.py`
- [ ] Am rulat `python generate_tokens.py` (o singură dată!)
- [ ] Am verificat că token-urile sunt în coloana J
- [ ] Am testat cu `python test_send.py`
- [ ] Am verificat că linkul din email funcționează
- [ ] Am verificat că Google Sheet se actualizează
- [ ] WEBAPP_URL este corect în `sheets_utils.py`
- [ ] Termenul limită este corect (17.11.2025) în `Code.gs`

---

## 🎉 Gata de Utilizare!

Sistemul este complet configurat și securizat. Poți trimite invitații cu încredere!

**Pentru suport**: Verifică logs în Apps Script → Executions

**Versiune**: 2.0 - Sistem cu Token-uri Unice  
**Data**: Octombrie 2025
