"""
CONFIRM SERVER - PRODUCTION READY
✅ Nu folosește Google Sheets (evită 502)
✅ Salvează confirmările în JSON local
✅ Trimite email de confirmare
✅ Design frumos, responsive
"""

from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime

app = Flask(__name__)

# SMTP Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

CONFIRMATIONS_FILE = 'confirmations.json'

def save_confirmation(token, response, persons=None):
    """Salvează confirmarea în JSON"""
    try:
        if os.path.exists(CONFIRMATIONS_FILE):
            with open(CONFIRMATIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        data.append({
            'token': token,
            'response': response,
            'persons': persons,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(CONFIRMATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Salvat: {response} - {persons}")
        return True
    except Exception as e:
        print(f"⚠️ Eroare salvare: {e}")
        return False

def send_email_fast(to_email, subject, html_body):
    """Trimite email"""
    try:
        print(f"📧 Email către {to_email}")
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Trimis!")
        return True
    except Exception as e:
        print(f"❌ Eroare: {e}")
        return False

@app.route('/')
def home():
    return "🚀 Server OK!"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token', '')
    resp = request.args.get('resp', '')
    persoane = request.args.get('persoane', '1')
    
    print(f"🎯 token={token[:15]}... resp={resp} pers={persoane}")
    
    if not token:
        return "Token lipsă!", 400
    
    if not resp:
        return render_template_string("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Confirmați - Concert UNBR</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial; text-align: center; padding: 20px;
       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
       min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.container { background: white; padding: 40px; border-radius: 20px;
             box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 500px; width: 100%; }
h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
h2 { color: #666; font-weight: normal; margin-bottom: 30px; font-size: 18px; }
.btn { display: block; width: 100%; padding: 18px; margin: 15px 0; border-radius: 12px;
       text-decoration: none; font-size: 18px; font-weight: bold; transition: 0.3s; }
.btn-yes { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white;
           box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4); }
.btn-yes:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6); }
.btn-no { background: linear-gradient(135deg, #f44336 0%, #da190b 100%); color: white;
          box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4); }
.btn-no:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(244, 67, 54, 0.6); }
.emoji { font-size: 48px; margin-bottom: 20px; }
</style>
</head><body>
<div class="container">
<div class="emoji">🎵</div>
<h1>Concert UNBR</h1>
<h2>24 noiembrie 2025 • Ateneul Român</h2>
<hr style="border: none; border-top: 2px solid #eee; margin: 30px 0;">
<p style="margin-bottom: 20px; color: #555; font-size: 16px;">Confirmați participarea:</p>
<a href="/confirm?token={{ token }}&resp=da&persoane=1" class="btn btn-yes">✔ Particip - 1 persoană</a>
<a href="/confirm?token={{ token }}&resp=da&persoane=2" class="btn btn-yes">✔ Particip - 2 persoane</a>
<a href="/confirm?token={{ token }}&resp=nu" class="btn btn-no">✖ Nu pot participa</a>
</div></body></html>""", token=token)
    
    if resp == 'da':
        save_confirmation(token, 'da', persoane)
        subject = "✅ Confirmare - Concert UNBR"
        html = f"""<html><body style="font-family: Arial; padding: 20px;">
<h2 style="color: #4CAF50;">✅ Confirmare primită!</h2>
<p>Am înregistrat participarea pentru <strong>{persoane} {'persoană' if persoane == '1' else 'persoane'}</strong>.</p>
<div style="background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 8px;">
<p><strong>📅</strong> 24 noiembrie 2025</p>
<p><strong>🕐</strong> 19:30</p>
<p><strong>📍</strong> Ateneul Român</p>
</div><p>Biletul vine în curând!</p></body></html>"""
        send_email_fast('alexandradragomir23@yahoo.com', subject, html)
        
        return """<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body { font-family: Arial; text-align: center; padding: 50px;
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;
display: flex; align-items: center; justify-content: center; margin: 0; }
.container { background: white; padding: 40px; border-radius: 20px;
box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 500px; }
h1 { color: #4CAF50; } .emoji { font-size: 64px; margin-bottom: 20px; }
</style></head><body><div class="container"><div class="emoji">✅</div>
<h1>Confirmare înregistrată!</h1><p style="font-size: 18px; color: #555;">
Am trimis email de confirmare. Vă mulțumim!</p></div></body></html>"""
    
    else:
        save_confirmation(token, 'nu', None)
        subject = "Răspuns înregistrat"
        html = """<html><body style="font-family: Arial; padding: 20px;">
<h2>Răspuns înregistrat</h2><p>Ne pare rău că nu puteți participa.</p></body></html>"""
        send_email_fast('alexandradragomir23@yahoo.com', subject, html)
        
        return """<html><head><meta charset="UTF-8"><style>
body { font-family: Arial; text-align: center; padding: 50px;
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;
display: flex; align-items: center; justify-content: center; margin: 0; }
.container { background: white; padding: 40px; border-radius: 20px;
box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 500px; }
</style></head><body><div class="container"><h1>Răspuns înregistrat</h1>
<p style="font-size: 18px; color: #555;">Vă mulțumim!</p></div></body></html>"""

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Port {port} | Email: {EMAIL_ADDRESS} | SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    app.run(host='0.0.0.0', port=port, debug=False)
