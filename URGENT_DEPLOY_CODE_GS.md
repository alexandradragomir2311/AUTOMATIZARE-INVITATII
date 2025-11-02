# 🚨 URGENT - ACTUALIZEAZĂ GOOGLE APPS SCRIPT

## PROBLEMA
Linkul de confirmare folosește Google Apps Script Web App care are versiunea VECHE cu:
- ❌ Deadline 17 noiembrie (trebuie 10 noiembrie)
- ❌ Trimite emailuri de pe Gmail (trebuie evenimente@unbr.ro)

## SOLUȚIA - RE-PUBLICĂ Code.gs

### Pasul 1: Deschide Google Apps Script
1. Mergi la: https://script.google.com
2. Deschide proiectul care conține Web App-ul pentru confirmări

### Pasul 2: Actualizează Codul
1. Deschide fișierul `Code.gs` din editor
2. **ȘTERGE TOT** conținutul vechi
3. **COPIAZĂ** tot conținutul din fișierul local `Code.gs` (cel actualizat)
4. **SALVEAZĂ** (Ctrl+S sau File → Save)

### Pasul 3: Re-publică Web App-ul
1. Click pe **Deploy** (butonul albastru din dreapta sus)
2. Selectează **Manage deployments**
3. Click pe iconița **Edit** (creion) lângă deployment-ul activ
4. La **Version**: selectează **New version**
5. Click **Deploy**
6. **IMPORTANT**: Copiază URL-ul nou (sau verifică că e același)

### Pasul 4: Verifică
1. Deschide un link de confirmare din email
2. Verifică că scrie **"Termen limită: 10 noiembrie 2025"**
3. Confirmă participarea → verifică că emailul vine de pe **evenimente@unbr.ro**

## CE AM MODIFICAT ÎN Code.gs

✅ **Deadline actualizat**: 
```javascript
const DEADLINE = new Date('2025-11-10T23:59:59');
```

✅ **Emailuri DEZACTIVATE din Google Apps Script**:
```javascript
function sendConfirmationEmail(email, response, persoane, nume) {
  Logger.log('sendConfirmationEmail DISABLED - emails handled by Flask SMTP server');
  // MailApp.sendEmail() - DEZACTIVAT
}
```

✅ **Toate mesajele actualizate** la "10 noiembrie 2025"

## ALTERNATIVĂ - FOLOSEȘTE DOAR SERVERUL LOCAL

Dacă preferi, poți:
1. **DEZACTIVA** complet Web App-ul din Google Apps Script
2. Folosește doar `confirm_server.py` (serverul Flask local)
3. **SCHIMBĂ** linkurile din invitații să meargă la serverul local

⚠️ **Serverul local trebuie să fie mereu pornit când trimiti invitații!**

---

**După re-publicare, sistemul va funcționa 100% corect! 🎉**
