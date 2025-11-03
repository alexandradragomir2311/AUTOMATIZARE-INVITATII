# 🔍 VERIFICĂ LOGURILE RENDER

## Pași:

1. **Deschide Render Dashboard:**
   - https://dashboard.render.com/
   - Selectează serviciul: **automatizare-invitatii-1**

2. **Click pe tab-ul "Logs"** (stânga)

3. **Caută mesajele acestea în logs:**

### ✅ Ce să cauți:

```
📧 SMTP mail.unbr.ro:25
```
→ Înseamnă că încearcă să trimită

```
✅ Email trimis: alexandradragomir23@yahoo.com
```
→ SUCCESS! Emailul a plecat

```
❌ Email error:
```
→ EROARE! Vezi ce scrie după

```
Connection refused
```
→ Render blochează portul

```
Timeout
```
→ Render blochează conexiunea

```
Authentication failed
```
→ Parolă greșită sau port greșit

```
📊 Update Sheet: token=
```
→ A încercat să actualizeze Sheet-ul

```
✅ Sheet updated: Da - 2 persoane
```
→ Sheet-ul s-a actualizat corect

```
✅ Linie nouă adăugată pentru persoana 2/2
```
→ Row-ul nou a fost adăugat

---

## 🎯 COPIAZĂ TOT textul din logs și trimite-mi-l aici!

Sau spune-mi ce mesaje vezi (✅ sau ❌)
