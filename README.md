# Automatizare Invitații cu Bilete și QR Code

Sistem complet de automatizare pentru generarea și trimiterea biletelor personalizate cu QR code.

## 📋 Flux de lucru

1. **Sheet1**: Lista inițială cu invitați
   - Adaugi invitații manual
   - Confirmă prezența (coloană "Confirmare": DA/NU)
   - Alocă locurile manual (coloană "Loc")

2. **Procesare automată** (rulare script):
   - Preia invitații confirmați din Sheet1
   - Generează serie unică pentru fiecare bilet
   - Generează QR code personalizat
   - Creează bilet PDF personalizat
   - Transferă datele în Sheet2
   - Trimite email cu biletul PDF atașat
   - Marchează ca "Procesat" în Sheet1

3. **Sheet2**: ALOCARI, LOCURI, BILETE, QR
   - Conține toți invitații procesați
   - Serie unică
   - Calea către QR code
   - Status email trimis

4. **Sheet3**: PREZENTA LA EVENIMENT
   - Se completează automat la scanarea QR code-ului
   - Marchează prezența cu ora sosirii

## 🚀 Instalare

### 1. Instalează dependențele Python:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install qrcode[pil] reportlab flask
```

### 2. Configurare Google Cloud Console:

1. Accesează [Google Cloud Console](https://console.cloud.google.com/)
2. Creează un proiect nou sau selectează unul existent
3. Activează API-urile:
   - Google Sheets API
   - Gmail API
4. Creează credențiale OAuth 2.0:
   - Du-te la "Credentials" → "Create Credentials" → "OAuth client ID"
   - Tip: Desktop app
   - Descarcă fișierul JSON
5. Redenumește fișierul în `credentials.json`
6. Plasează în folderul `credentials/`

### 3. Configurare Google Sheets:

1. Creează un Google Sheet nou sau folosește unul existent
2. Asigură-te că ai 3 sheet-uri:
   - **Sheet1**: Invitați inițiali (cu coloane: Nume, Prenume, Email, Confirmare, Loc)
   - **Sheet2**: Bilete generate
   - **Sheet3**: Prezență eveniment
3. Copiază ID-ul spreadsheet-ului din URL
4. Actualizează `SPREADSHEET_ID` în `sheets_utils.py`

### 4. Structura Sheet1 (recomandată):

| Nume | Prenume | Email | Confirmare | Loc | Procesat |
|------|---------|-------|------------|-----|----------|
| Popescu | Ion | ion@email.com | DA | A12 | |
| Ionescu | Maria | maria@email.com | DA | A13 | |

### 5. Structura Sheet2 (automată):

| Nume | Prenume | Email | Loc | Serie | QR Code | Status | Email Trimis |
|------|---------|-------|-----|-------|---------|--------|--------------|

## 📝 Utilizare

### Rulare completă (procesare invitații):

```bash
python main.py
```

Acest script va:
- ✓ Citi invitații confirmați din Sheet1
- ✓ Genera serie unică + QR code + PDF pentru fiecare
- ✓ Transfera în Sheet2
- ✓ Trimite email cu biletul PDF
- ✓ Actualiza statusurile

### Server Flask (pentru confirmări online - opțional):

```bash
python flask_server.py
```

## 📂 Structura fișierelor generate:

```
static/
├── qr_codes/
│   ├── EVT-20251028-ABC12345.png
│   └── EVT-20251028-DEF67890.png
└── tickets/
    ├── Bilet_EVT-20251028-ABC12345.pdf
    └── Bilet_EVT-20251028-DEF67890.pdf
```

## 🔧 Personalizare

### Modifică designul biletului PDF:
Editează funcția `generate_ticket_pdf()` în `ticket_generator.py`

### Modifică template-ul de email:
Editează funcția `send_invitation_with_ticket()` în `gmail_utils.py`

### Modifică formatul seriei:
Editează funcția `generate_unique_series()` în `ticket_generator.py`

## 🎯 Verificare QR Code la eveniment

Pentru a scana QR code-urile și marca prezența, poți crea o aplicație mobilă sau web care:
1. Scanează QR code-ul
2. Extrage seria biletului
3. Verifică în Sheet2 dacă seria există
4. Adaugă înregistrare în Sheet3 cu ora sosirii

## ⚠️ Note importante

- Prima rulare va deschide browserul pentru autentificare Google
- Token-urile vor fi salvate în `credentials/token.json` și `credentials/token_gmail.json`
- Nu șterge aceste fișiere după autentificare
- Asigură-te că Sheet1 are coloanele "Confirmare" și "Loc" completate corect

## 🆘 Troubleshooting

### "Eroare la citirea Sheet1":
- Verifică că SPREADSHEET_ID este correct
- Verifică că ai dat share la spreadsheet cu contul Google folosit

### "Eroare la trimiterea emailului":
- Verifică că Gmail API este activat
- Verifică că ai autentificat corect

### "QR code nu se generează":
- Verifică că folderul `static/` are permisiuni de scriere
- Verifică că biblioteca `qrcode` este instalată: `pip install qrcode[pil]`

## 📞 Suport

Pentru probleme sau întrebări, verifică fișierele de log generate de script.
