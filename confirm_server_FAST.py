"""
CONFIRM SERVER - VERSIUNE ULTRA SIMPLĂ
Doar trimite email, fără Google Sheets!
"""

from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# SMTP DIRECT
SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'WsmM6$372F')

def send_email_fast(to_email, subject, html_body):
    """Trimite email RAPID fără verificări"""
    try:
        print(f"📧 TRIMIT email către {to_email}")
        print(f"📧 SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            print(f"🔐 Login cu {EMAIL_ADDRESS}...")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print("✅ Autentificat!")
            server.send_message(msg)
            print("✅ EMAIL TRIMIS!")
            return True
            
    except Exception as e:
        print(f"❌ EROARE: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/')
def home():
    return "🚀 Server FAST activ!"

@app.route('/confirm', methods=['GET'])
def confirm():
    """Procesează confirmarea - VERSIUNE RAPIDĂ"""
    token = request.args.get('token', '')
    resp = request.args.get('resp', '')
    persoane = request.args.get('persoane', '1')
    
    print(f"\n🎯 CONFIRMARE: token={token[:20]}... resp={resp} persoane={persoane}")
    
    # Dacă nu e răspuns, arată butoanele
    if not resp:
        return render_template_string("""
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8">
                <title>Confirmați prezența</title>
                <style>
                    body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
                    .btn { display: inline-block; padding: 15px 30px; margin: 10px; 
                           border-radius: 5px; text-decoration: none; font-size: 18px; }
                    .btn-yes { background: #4CAF50; color: white; }
                    .btn-no { background: #f44336; color: white; }
                    .btn:hover { opacity: 0.8; }
                </style>
            </head><body>
                <h1>🎵 Concert UNBR - 24 noiembrie 2025</h1>
                <h2>Confirmați participarea:</h2>
                <a href="/confirm?token={{ token }}&resp=da&persoane=1" class="btn btn-yes">✔ 1 persoană</a>
                <a href="/confirm?token={{ token }}&resp=da&persoane=2" class="btn btn-yes">✔ 2 persoane</a>
                <br><br>
                <a href="/confirm?token={{ token }}&resp=nu" class="btn btn-no">✖ Nu particip</a>
            </body></html>
        """, token=token)
    
    # Procesează răspunsul - TRIMITE EMAIL DIRECT!
    if resp == 'da':
        subject = "✅ Confirmare participare - Concert UNBR"
        html_body = f"""
        <html><body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #4CAF50;">✅ Vă mulțumim pentru confirmare!</h2>
            <p>Am înregistrat participarea pentru <strong>{persoane} {'persoană' if persoane == '1' else 'persoane'}</strong>.</p>
            <div style="background: #f5f5f5; padding: 15px; margin: 20px 0;">
                <p><strong>📅 Data:</strong> 24 noiembrie 2025</p>
                <p><strong>🕐 Ora:</strong> 19:30</p>
                <p><strong>📍 Locație:</strong> Ateneul Român</p>
            </div>
            <p>Veți primi biletul în curând!</p>
        </body></html>
        """
        # Trimite la adresa de test (sau extrage din Sheet dacă vrei)
        send_email_fast('alexandradragomir23@yahoo.com', subject, html_body)
        
        return render_template_string("""
            <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #4CAF50;">✅ Confirmare înregistrată!</h1>
                <p style="font-size: 18px;">Am trimis un email de confirmare.</p>
                <p style="color: #666;">Vă mulțumim!</p>
            </body></html>
        """)
    
    else:  # nu particip
        subject = "Răspuns înregistrat - Concert UNBR"
        html_body = """
        <html><body style="font-family: Arial; padding: 20px;">
            <h2>Răspuns înregistrat</h2>
            <p>Ne pare rău că nu puteți participa. Am înregistrat răspunsul.</p>
        </body></html>
        """
        send_email_fast('alexandradragomir23@yahoo.com', subject, html_body)
        
        return render_template_string("""
            <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>Răspuns înregistrat</h1>
                <p style="font-size: 18px;">Vă mulțumim pentru răspuns!</p>
            </body></html>
        """)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Server pornit pe port {port}")
    print(f"📧 Email: {EMAIL_ADDRESS}")
    print(f"📧 SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    app.run(host='0.0.0.0', port=port, debug=False)
