# 🚀 GHID COMPLET: Deploy pe VPS Contabo

## ✅ Ce ai făcut până acum:
- [x] Cont Contabo creat
- [x] VPS comandat (Cloud VPS 10: 8GB RAM, 75GB Storage)
- [ ] **AȘTEAPTĂ EMAIL** cu IP și parolă (5-30 minute)

---

## 📧 Pasul 1: Primire detalii VPS

Vei primi email de la Contabo cu:
- **IP Address:** (ex: `123.45.67.89`)
- **Username:** `root`
- **Password:** (parola generată)

**⚠️ NOTEAZĂ-LE UNDEVA SIGUR!**

---

## 🔌 Pasul 2: Conectare SSH (din Windows PowerShell)

```powershell
ssh root@<IP-ul-tau>
# Exemplu: ssh root@123.45.67.89
```

La prima conectare:
- Va întreba: `Are you sure you want to continue connecting?` → scrie `yes`
- Apoi introdu parola primită pe email
- Dacă îți cere să schimbi parola → alege una nouă și sigură

---

## 🐍 Pasul 3: Instalare Python și dependențe

Rulează comenzile una câte una:

```bash
# 1. Update sistem
apt update && apt upgrade -y

# 2. Instalare Python 3.11, pip, git
apt install python3 python3-pip python3-venv git nano -y

# 3. Verifică versiunea Python
python3 --version
# Ar trebui să afișeze: Python 3.10+ sau 3.11+
```

---

## 📂 Pasul 4: Clone repository GitHub

```bash
# 1. Mergi în /root
cd /root

# 2. Clonează repo-ul
git clone https://github.com/alexandradragomir2311/AUTOMATIZARE-INVITATII.git

# 3. Intră în folder
cd AUTOMATIZARE-INVITATII

# 4. Creează virtual environment
python3 -m venv venv

# 5. Activează virtual environment
source venv/bin/activate

# 6. Instalare dependențe
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Pasul 5: Upload credentials (din Windows PowerShell LOCAL)

**Deschide un PowerShell NOU pe Windows (nu închide cel cu SSH!):**

```powershell
# Navighează la folder-ul proiectului
cd "C:\Users\40740\Desktop\AUTOMATIZARE INVITATII - Cont UNBR"

# Upload token.pickle (IMPORTANT!)
scp credentials/token.pickle root@<IP-VPS>:/root/AUTOMATIZARE-INVITATII/credentials/
# Exemplu: scp credentials/token.pickle root@123.45.67.89:/root/AUTOMATIZARE-INVITATII/credentials/

# Upload email_credentials.txt
scp credentials/email_credentials.txt root@<IP-VPS>:/root/AUTOMATIZARE-INVITATII/credentials/
```

**La fiecare comandă SCP:**
- Va cere parola VPS-ului
- Introdu parola root primită de la Contabo

---

## ⚙️ Pasul 6: Configurare environment variables pe VPS

**În SSH (pe VPS), rulează:**

```bash
# Creează fișier .env
nano .env
```

**Adaugă (copiază-paste):**
```
EMAIL_ADDRESS=evenimente@unbr.ro
EMAIL_PASSWORD=WsmM6$372F
SMTP_SERVER=mail.unbr.ro
SMTP_PORT=587
SMTP_USE_TLS=true
```

**Salvează:**
- `Ctrl + O` (save)
- `Enter` (confirm)
- `Ctrl + X` (exit)

---

## 🔄 Pasul 7: Actualizare WEBAPP_URL

**Pe LAPTOP (Windows), actualizează fișierul:**

Schimbă în `sheets_utils.py` linia 38:
```python
WEBAPP_URL = 'http://<IP-VPS>:5000/confirm'
# Exemplu: WEBAPP_URL = 'http://123.45.67.89:5000/confirm'
```

**Apoi push pe GitHub:**
```powershell
git add sheets_utils.py
git commit -m "UPDATE: WEBAPP_URL with VPS IP"
git push origin main
```

**Pe VPS (SSH), pull schimbările:**
```bash
cd /root/AUTOMATIZARE-INVITATII
git pull origin main
```

---

## 🚀 Pasul 8: Rulare server permanent (PM2)

**Pe VPS (SSH):**

```bash
# 1. Instalare Node.js și PM2
apt install nodejs npm -y
npm install -g pm2

# 2. Activează virtual environment (dacă nu e activ)
cd /root/AUTOMATIZARE-INVITATII
source venv/bin/activate

# 3. Pornește serverul cu PM2
pm2 start confirm_server.py --interpreter python3 --name unbr-confirm

# 4. Configurare auto-restart la reboot
pm2 startup
# Copiază comanda afișată și rulează-o

pm2 save

# 5. Verifică status
pm2 status
pm2 logs unbr-confirm
```

---

## 🔥 Pasul 9: Configurare Firewall

**Pe VPS (SSH):**

```bash
# Instalare UFW (firewall)
apt install ufw -y

# Permite SSH (important!)
ufw allow 22/tcp

# Permite portul 5000 (Flask)
ufw allow 5000/tcp

# Activează firewall
ufw enable

# Verifică status
ufw status
```

---

## ✅ Pasul 10: TEST FINAL

### Test 1: Verifică serverul rulează
```bash
curl http://localhost:5000/
# Ar trebui să afișeze: OK
```

### Test 2: Trimite invitație de test
```bash
cd /root/AUTOMATIZARE-INVITATII
source venv/bin/activate
python test_send.py
```

### Test 3: Accesează link de confirmare
- Deschide email-ul primit
- Click pe link: `http://<IP-VPS>:5000/confirm?token=...`
- Confirmă participarea
- ✅ Verifică Google Sheets s-a actualizat
- ✅ Verifică ai primit email de confirmare pe yahoo
- ✅ Verifică ai primit notificare pe evenimente@unbr.ro

---

## 🎯 SISTEM COMPLET FUNCȚIONAL!

✅ **Invitații:** Trimise de pe `evenimente@unbr.ro` (rulează local)
✅ **Link confirmări:** `http://<IP-VPS>:5000/confirm` (24/7 online)
✅ **Email confirmări:** Trimise automat de pe `evenimente@unbr.ro` (VPS)
✅ **Google Sheets:** Actualizare instantanee
✅ **Fără restricții SMTP:** Totul funcționează perfect!

---

## 📞 AJUTOR SUPLIMENTAR

Dacă ai probleme la vreun pas, verifică:
- `pm2 logs unbr-confirm` - loguri server
- `pm2 restart unbr-confirm` - restart server
- `systemctl status ufw` - status firewall

---

## 🔄 COMENZI UTILE

```bash
# Restart server
pm2 restart unbr-confirm

# Stop server
pm2 stop unbr-confirm

# Vizualizează loguri live
pm2 logs unbr-confirm --lines 100

# Pull ultimele modificări de pe GitHub
cd /root/AUTOMATIZARE-INVITATII
git pull origin main
pm2 restart unbr-confirm
```

---

**SUCCES! 🚀**
