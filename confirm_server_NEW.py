"""
SERVER SIMPLU PENTRU CONFIRMĂRI - VERSIUNE MINIMALISTĂ
"""
from flask import Flask, request, render_template_string
import gspread
from datetime import datetime
from sheets_utils import SPREADSHEET_ID, get_credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os

app = Flask(__name__)
SHEET_NAME = 'INVITATII SI CONFIRMARI'
DEADLINE = datetime(2025, 11, 10, 23, 59, 59)

# Email config - DIRECT!
SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

# Dacă nu e pe Render, citește din fișier
if not EMAIL_PASSWORD:
    try:
        with open('credentials/email_credentials.txt', 'r') as f:
            EMAIL_PASSWORD = f.read().strip()
    except:
        pass

def send_email_direct(to_email: str, subject: str, html_body: str):
    """Trimite email DIRECT prin SMTP - fără complicații!"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(('Evenimente UNBR', EMAIL_ADDRESS))
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email trimis către {to_email}")
        return True
    except Exception as e:
        print(f"❌ Eroare email: {e}")
        return False

# Template simplu pentru confirmare
SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmare înregistrată</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
        .box { background: white; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #4CAF50; }
        p { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="box">
        <h1>✅ {{ title }}</h1>
        <p>{{ message }}</p>
        <p style="margin-top: 30px; font-size: 14px; color: #999;">
            Veți primi în curând un email de confirmare.
        </p>
    </div>
</body>
</html>
"""

@app.route('/confirm', methods=['GET'])
def confirm():
    """Handler SIMPLU pentru confirmări"""
    token = request.args.get('token')
    resp = request.args.get('resp')
    persoane = request.args.get('persoane')
    
    print(f"\n{'='*80}")
    print(f"🎯 CONFIRMARE PRIMITĂ: token={token}, resp={resp}, persoane={persoane}")
    print(f"{'='*80}\n")
    
    if not token:
        return "Token lipsă!", 400
    
    # Verifică deadline
    if datetime.now() > DEADLINE:
        return render_template_string(SUCCESS_TEMPLATE, 
            title="Termen expirat",
            message="Termenul limită pentru confirmări a expirat.")
    
    try:
        # Conectează la Google Sheets
        print("📊 Conectare la Google Sheets...")
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        print("✅ Conectat la Sheet!")
        
        # Citește datele
        all_data = sheet.get_all_values()
        print(f"📋 Am citit {len(all_data)} rânduri")
        
        # Găsește invitatul după token
        row_index = None
        guest_name = None
        guest_email = None
        
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 9 and row[9] == token:
                row_index = i
                guest_name = row[0]
                guest_email = row[4]
                print(f"👤 Găsit: {guest_name} ({guest_email})")
                break
        
        if not row_index:
            return "Token invalid!", 404
        
        # Dacă nu are răspuns, arată pagina de selecție
        if not resp:
            return render_template_string("""
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8"><title>Confirmați</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
                .btn { padding: 20px 40px; margin: 10px; font-size: 18px; border: none; 
                       border-radius: 8px; cursor: pointer; text-decoration: none; 
                       display: inline-block; color: white; }
                .btn-yes { background: #4CAF50; }
                .btn-no { background: #f44336; }
            </style></head><body>
                <h1>Confirmați participarea</h1>
                <p>Concert UNBR - 24 noiembrie 2025</p>
                <a href="/confirm?token={{ token }}&resp=da&persoane=1" class="btn btn-yes">1 persoană</a>
                <a href="/confirm?token={{ token }}&resp=da&persoane=2" class="btn btn-yes">2 persoane</a>
                <br><br>
                <a href="/confirm?token={{ token }}&resp=nu" class="btn btn-no">Nu particip</a>
            </body></html>
            """, token=token)
        
        # Procesează răspunsul
        if resp == 'da':
            nr_pers = f"{persoane} {'persoană' if persoane == '1' else 'persoane'}"
            sheet.update_cell(row_index, 8, f"✔ Da - {nr_pers}")
            sheet.update_cell(row_index, 9, nr_pers)
            print(f"✅ Sheet actualizat: Da - {nr_pers}")
            
            # TRIMITE EMAIL CONFIRMARE - DIRECT!
            print(f"📧 Trimit email confirmare către {guest_email}...")
            subject = "Confirmare participare - Concert UNBR"
            html_body = f"""
            <html><body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #4CAF50;">Vă mulțumim pentru confirmare!</h2>
                <p>Bună ziua {guest_name},</p>
                <p>Am înregistrat participarea dumneavoastră pentru <strong>{nr_pers}</strong> 
                la concertul omagial UNBR.</p>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>📅 Data:</strong> 24 noiembrie 2025</p>
                    <p><strong>🕐 Ora:</strong> 19:30</p>
                    <p><strong>📍 Locație:</strong> Ateneul Român, București</p>
                </div>
                <p>Veți primi în curând biletul de intrare.</p>
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    Cu stimă,<br>
                    Echipa UNBR
                </p>
            </body></html>
            """
            
            if send_email_direct(guest_email, subject, html_body):
                print("✅ EMAIL TRIMIS CU SUCCES!")
            else:
                print("⚠️ Email nu s-a trimis!")
            
            return render_template_string(SUCCESS_TEMPLATE,
                title="Participare confirmată!",
                message=f"Am înregistrat participarea pentru {nr_pers}. Veți primi un email de confirmare în curând.")
        
        else:  # resp == 'nu'
            sheet.update_cell(row_index, 8, '❌ Nu')
            sheet.update_cell(row_index, 9, '-')
            print(f"✅ Sheet actualizat: Nu particip")
            
            # TRIMITE EMAIL DECLINARE - DIRECT!
            print(f"📧 Trimit email declinare către {guest_email}...")
            subject = "Răspuns înregistrat - Concert UNBR"
            html_body = f"""
            <html><body style="font-family: Arial; padding: 20px;">
                <h2>Răspuns înregistrat</h2>
                <p>Bună ziua {guest_name},</p>
                <p>Ne pare rău că nu puteți participa la acest eveniment. 
                Am înregistrat răspunsul dumneavoastră.</p>
                <p>Sperăm să vă revedem la următoarele evenimente UNBR!</p>
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    Cu stimă,<br>
                    Echipa UNBR
                </p>
            </body></html>
            """
            
            send_email_direct(guest_email, subject, html_body)
            
            return render_template_string(SUCCESS_TEMPLATE,
                title="Răspuns înregistrat",
                message="Am înregistrat că nu puteți participa. Vă mulțumim pentru răspuns!")
    
    except Exception as e:
        print(f"❌ EROARE: {e}")
        import traceback
        traceback.print_exc()
        return f"Eroare: {str(e)}", 500

if __name__ == '__main__':
    print("\n🚀 SERVER PORNIT - Versiune SIMPLIFICATĂ")
    print(f"📧 Email: {EMAIL_ADDRESS}")
    print(f"🔐 Parolă: {'✅ Setată' if EMAIL_PASSWORD else '❌ LIPSĂ!'}\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
