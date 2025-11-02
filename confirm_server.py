"""
CONFIRM SERVER - ASYNC EMAIL + GOOGLE SHEETS
Trimite email în background, răspunde INSTANT, update Google Sheet
"""

from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
import sys

# Import sheets_utils pentru Google Sheets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheets_utils import get_credentials
import gspread

app = Flask(__name__)

# SMTP evenimente@unbr.ro - PORT 587 cu STARTTLS
SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SPREADSHEET_ID = '1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg'
SHEET_NAME = 'INVITATII SI CONFIRMARI'

def update_sheet_background(token, response, persons=None):
    """Update Google Sheet în background"""
    def update():
        try:
            print(f"📊 Update Sheet: token={token[:15]}... resp={response} pers={persons}", flush=True)
            creds = get_credentials()
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            sheet = spreadsheet.worksheet(SHEET_NAME)
            all_data = sheet.get_all_values()
            print(f"📊 Loaded {len(all_data)} rows from sheet", flush=True)
            
            # Găsește row după token
            for i, row in enumerate(all_data[1:], start=2):
                if len(row) > 9 and row[9] == token:
                    print(f"📊 Found token in row {i}", flush=True)
                    if response == 'da':
                        sheet.update_cell(i, 8, f"✔ Da - {persons}")
                        sheet.update_cell(i, 9, persons)
                        print(f"✅ Sheet updated: Da - {persons} persoane", flush=True)
                        
                        # ⭐ LOGIC NOUĂ: Dacă 2 persoane, adaugă linie nouă
                        if persons == '2':
                            print(f"👥 Confirmare 2 persoane - adaug linie nouă...", flush=True)
                            # Copiază date din row original
                            nume = row[0] if len(row) > 0 else ''
                            prenume = row[1] if len(row) > 1 else ''
                            functie = row[2] if len(row) > 2 else ''
                            institutie = row[3] if len(row) > 3 else ''
                            email = row[4] if len(row) > 4 else ''
                            
                            # Adaugă row nou la sfârșit
                            new_row = [nume, prenume, functie, institutie, email, '', '', 
                                      'Confirmare 2/2', '1', token]
                            sheet.append_row(new_row)
                            print(f"✅ Linie nouă adăugată pentru persoana 2/2", flush=True)
                    else:
                        sheet.update_cell(i, 8, '❌ Nu')
                        sheet.update_cell(i, 9, '-')
                        print(f"✅ Sheet updated: Nu particip", flush=True)
                    return
            print(f"⚠️ Token not found in Sheet", flush=True)
        except Exception as e:
            print(f"❌ Sheet error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching Sheet update thread...", flush=True)
    thread = threading.Thread(target=update, daemon=True)
    thread.start()
    print(f"🔄 Sheet thread started", flush=True)

def get_email_from_sheet(token):
    """Găsește emailul din Sheet după token"""
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        all_data = sheet.get_all_values()
        
        for row in all_data[1:]:
            if len(row) > 9 and row[9] == token:
                return row[4] if len(row) > 4 else 'alexandradragomir23@yahoo.com'
        return 'alexandradragomir23@yahoo.com'
    except:
        return 'alexandradragomir23@yahoo.com'

def send_email_background(to_email, subject, html_body):
    """Trimite email în thread separat - evenimente@unbr.ro SMTP"""
    def send():
        try:
            print(f"📧 Preparing email to {to_email}...", flush=True)
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # SMTP standard cu STARTTLS
            print(f"📧 Connecting to SMTP {SMTP_SERVER}:{SMTP_PORT}...", flush=True)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                print(f"📧 Connected! Starting TLS={SMTP_USE_TLS}...", flush=True)
                if SMTP_USE_TLS:
                    server.starttls()
                    print(f"📧 TLS started, logging in...", flush=True)
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                print(f"📧 Logged in, sending...", flush=True)
                server.send_message(msg)
            print(f"✅ Email trimis: {to_email}", flush=True)
        except Exception as e:
            print(f"❌ Email error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching email send thread...", flush=True)
    thread = threading.Thread(target=send, daemon=True)
    thread.start()
    print(f"🔄 Email thread started", flush=True)

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
        print(f"🎯 CONFIRMARE DA - persoane={persoane}, token={token[:15]}...", flush=True)
        
        # UPDATE GOOGLE SHEET ÎN BACKGROUND
        print(f"📊 Starting Sheet update thread...", flush=True)
        update_sheet_background(token, 'da', persoane)
        
        # GĂSEȘTE EMAIL DIN SHEET
        print(f"📧 Getting email from sheet...", flush=True)
        guest_email = get_email_from_sheet(token)
        print(f"📧 Found email: {guest_email}", flush=True)
        
        # TRIMITE EMAIL ÎN BACKGROUND
        print(f"📧 Starting email send thread...", flush=True)
        send_email_background(
            guest_email,
            '✅ Confirmare - Concert UNBR',
            f'<h2>Confirmat pentru {persoane} {'persoană' if persoane == '1' else 'persoane'}</h2><p>Vă mulțumim! Veți primi biletul în curând.</p>'
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
        # UPDATE GOOGLE SHEET ÎN BACKGROUND
        update_sheet_background(token, 'nu', None)
        
        # GĂSEȘTE EMAIL DIN SHEET
        guest_email = get_email_from_sheet(token)
        
        # TRIMITE EMAIL ÎN BACKGROUND
        send_email_background(
            guest_email,
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
