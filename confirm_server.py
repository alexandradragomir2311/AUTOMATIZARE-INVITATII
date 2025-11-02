"""
CONFIRM SERVER - ASYNC EMAIL
Trimite email în background, răspunde INSTANT
"""

from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading

app = Flask(__name__)

SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

def send_email_background(to_email, subject, html_body):
    """Trimite email în thread separat"""
    def send():
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"✅ Email trimis: {to_email}")
        except Exception as e:
            print(f"❌ Email error: {e}")
    
    # Start în background thread
    thread = threading.Thread(target=send, daemon=True)
    thread.start()

@app.route('/')
def home():
    return "OK"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token', '')
    resp = request.args.get('resp', '')
    persoane = request.args.get('persoane', '1')
    
    if not token:
        return "Error", 400
    
    if not resp:
        return render_template_string("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confirmare</title>
<style>
body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
.box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 400px; }
h1 { color: #333; margin: 0 0 20px 0; }
h2 { color: #666; font-weight: normal; margin: 0 0 30px 0; }
a { display: block; padding: 15px; margin: 10px 0; background: #4CAF50; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
a:hover { opacity: 0.9; }
.no { background: #f44336; }
</style>
</head><body>
<div class="box">
<h1>🎵 Concert UNBR</h1>
<h2>24 noiembrie 2025</h2>
<a href="/confirm?token={{ token }}&resp=da&persoane=1">✔ Particip - 1</a>
<a href="/confirm?token={{ token }}&resp=da&persoane=2">✔ Particip - 2</a>
<a href="/confirm?token={{ token }}&resp=nu" class="no">✖ Nu particip</a>
</div></body></html>
        """, token=token)
    
    if resp == 'da':
        # TRIMITE EMAIL ÎN BACKGROUND - NU BLOCA
        send_email_background(
            'alexandradragomir23@yahoo.com',
            '✅ Confirmare - Concert UNBR',
            f'<h2>Confirmat pentru {persoane} persoane</h2><p>Vă mulțumim!</p>'
        )
        
        # RĂSPUNDE IMEDIAT
        return render_template_string("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
.box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 400px; }
h1 { color: #4CAF50; margin: 0; }
.emoji { font-size: 64px; margin-bottom: 20px; }
p { color: #666; }
</style>
</head><body>
<div class="box">
<div class="emoji">✅</div>
<h1>Confirmare primită!</h1>
<p>Am înregistrat participarea pentru {{ persoane }} persoane.</p>
<p style="margin-top: 20px; font-size: 14px; color: #999;">Email de confirmare vine în curând...</p>
</div></body></html>
        """, persoane=persoane)
    
    else:
        # TRIMITE EMAIL ÎN BACKGROUND
        send_email_background(
            'alexandradragomir23@yahoo.com',
            'Răspuns - Concert UNBR',
            '<h2>Răspuns înregistrat</h2><p>Ne pare rău că nu puteți participa.</p>'
        )
        
        # RĂSPUNDE IMEDIAT
        return render_template_string("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
.box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 400px; }
h1 { color: #333; }
p { color: #666; }
</style>
</head><body>
<div class="box">
<h1>Răspuns înregistrat</h1>
<p>Vă mulțumim pentru răspuns!</p>
</div></body></html>
        """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
