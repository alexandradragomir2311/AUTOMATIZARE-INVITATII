"""
CONFIRM SERVER - ASYNC EMAIL + GOOGLE SHEETS
Trimite email în background prin Gmail API, răspunde INSTANT, update Google Sheet
"""

from flask import Flask, request, render_template_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
import sys
import base64

# Import sheets_utils pentru Google Sheets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheets_utils import get_credentials
import gspread
from googleapiclient.discovery import build

app = Flask(__name__)

# Gmail API pentru Render (funcționează prin HTTPS!) + Headers personalizate evenimente@unbr.ro
DISPLAY_EMAIL = 'evenimente@unbr.ro'  # Ce apare în From/Reply-To
SPREADSHEET_ID = '1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg'
SHEET_NAME = 'INVITATII SI CONFIRMARI'

def get_gmail_service():
    """Creează serviciul Gmail API folosind același credential ca și Sheets"""
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        print(f"✅ Gmail API service created", flush=True)
        return service
    except Exception as e:
        print(f"❌ Error creating Gmail service: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

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
                        print(f"🔍 Checking persons: '{persons}' (type: {type(persons).__name__})", flush=True)
                        if str(persons) == '2':
                            print(f"👥 Confirmare 2 persoane - adaug linie nouă...", flush=True)
                            
                            # Actualizează row-ul curent ca "Persoana 1/2"
                            sheet.update_cell(i, 8, "✔ Da - Persoana 1/2")
                            print(f"✅ Row {i} actualizat: Persoana 1/2", flush=True)
                            
                            # Verifică dacă următorul row există deja (Persoana 2/2)
                            has_person2 = False
                            if i < len(all_data):
                                next_row = all_data[i] if i < len(all_data) else None
                                if next_row and len(next_row) > 7 and "Persoana 2/2" in str(next_row[7]):
                                    has_person2 = True
                                    print(f"⚠️ Persoana 2/2 deja există în row {i+1}", flush=True)
                            
                            if not has_person2:
                                # Inserează row NOU după cel curent
                                sheet.insert_row([''] * 10, i + 1)
                                print(f"✅ Row nou inserat la poziția {i+1}", flush=True)
                                
                                # Copiază datele din row-ul original (coloanele A-G)
                                for col_idx in range(1, 8):  # Coloanele 1-7 (A-G)
                                    val = sheet.cell(i, col_idx).value
                                    sheet.update_cell(i + 1, col_idx, val)
                                
                                # Setează pentru Persoana 2/2 - ACELAȘI TOKEN!
                                sheet.update_cell(i + 1, 8, "✔ Da - Persoana 2/2")
                                sheet.update_cell(i + 1, 9, "Persoana 2")
                                sheet.update_cell(i + 1, 10, token)  # Același token!
                                print(f"✅ Linie nouă completată pentru Persoana 2/2", flush=True)
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
    return thread  # Returnează thread-ul pentru tracking

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

def get_name_from_sheet(token):
    """Găsește numele complet din Sheet după token"""
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        all_data = sheet.get_all_values()
        
        for row in all_data[1:]:
            if len(row) > 9 and row[9] == token:
                nume = row[0] if len(row) > 0 else ''
                prenume = row[1] if len(row) > 1 else ''
                return f"{nume} {prenume}".strip()
        return 'Invitat'
    except:
        return 'Invitat'

def send_notification_to_admin(guest_name, guest_email, persons, response_type):
    """Trimite notificare către evenimente@unbr.ro când cineva confirmă - GMAIL API"""
    def send():
        try:
            print(f"📧 Preparing admin notification via Gmail API...", flush=True)
            
            # Construiește mesajul
            if response_type == 'confirmare':
                subject = f"✅ CONFIRMARE: {guest_name} - {persons} {'persoană' if persons == '1' else 'persoane'}"
                html_body = f"""
                <html><body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #4CAF50;">✅ Confirmare Primită</h2>
                <p><strong>Nume:</strong> {guest_name}</p>
                <p><strong>Email:</strong> {guest_email}</p>
                <p><strong>Număr persoane:</strong> {persons}</p>
                <p><strong>Data confirmării:</strong> {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Verificați Google Sheet pentru detalii complete.</p>
                </body></html>
                """
            else:
                subject = f"❌ DECLINARE: {guest_name}"
                html_body = f"""
                <html><body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #f44336;">❌ Nu Participă</h2>
                <p><strong>Nume:</strong> {guest_name}</p>
                <p><strong>Email:</strong> {guest_email}</p>
                <p><strong>Data răspunsului:</strong> {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Verificați Google Sheet pentru detalii complete.</p>
                </body></html>
                """
            
            msg = MIMEMultipart('alternative')
            msg['From'] = f"UNBR Evenimente <{DISPLAY_EMAIL}>"  # Apare ca evenimente@unbr.ro
            msg['Reply-To'] = DISPLAY_EMAIL  # Reply-urile merg la evenimente@unbr.ro
            msg['To'] = DISPLAY_EMAIL  # Trimite către evenimente@unbr.ro
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Trimite prin GMAIL API (funcționează pe Render!)
            print(f"📧 Getting Gmail API service...", flush=True)
            service = get_gmail_service()
            if not service:
                print(f"❌ Failed to get Gmail service", flush=True)
                return
            
            print(f"📧 Encoding message...", flush=True)
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            
            print(f"📧 Sending via Gmail API...", flush=True)
            service.users().messages().send(userId='me', body=send_message).execute()
            print(f"✅ Notificare trimisă către {DISPLAY_EMAIL} (via Gmail API)", flush=True)
        except Exception as e:
            print(f"❌ Admin notification error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching admin notification thread...", flush=True)
    thread = threading.Thread(target=send, daemon=True)
    thread.start()
    print(f"🔄 Admin notification thread started", flush=True)
    return thread  # Returnează thread-ul pentru tracking

def send_confirmation_email_to_guest(to_email, guest_name, persons):
    """Trimite email de CONFIRMARE către invitat - GMAIL API cu headers evenimente@unbr.ro"""
    def send():
        try:
            print(f"📧 Preparing confirmation email to {to_email}...", flush=True)
            
            subject = f"✅ Confirmare participare - Concert UNBR 24 noiembrie 2025"
            html_body = f"""
            <html><body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #4CAF50; text-align: center;">✅ Confirmare Primită</h1>
                <p style="font-size: 16px;">Bună ziua <strong>{guest_name}</strong>,</p>
                <p style="font-size: 16px;">Am înregistrat confirmarea dumneavoastră pentru <strong>{persons} {'persoană' if persons == '1' else 'persoane'}</strong> la concertul din 24 noiembrie 2025.</p>
                
                <div style="background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333;">📅 Detalii eveniment:</h3>
                    <p style="margin: 5px 0;"><strong>Data:</strong> 24 noiembrie 2025</p>
                    <p style="margin: 5px 0;"><strong>Organizator:</strong> UNBR</p>
                    <p style="margin: 5px 0;"><strong>Persoane confirmate:</strong> {persons}</p>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">Vă așteptăm cu drag!</p>
                <p style="font-size: 14px; color: #666;">Cu stimă,<br><strong>Echipa UNBR</strong></p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #999; text-align: center;">Acest email a fost trimis automat. Pentru întrebări, răspundeți la acest email.</p>
            </div>
            </body></html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['From'] = f"UNBR Evenimente <{DISPLAY_EMAIL}>"  # Apare ca evenimente@unbr.ro
            msg['Reply-To'] = DISPLAY_EMAIL  # Reply-urile merg la evenimente@unbr.ro
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Trimite prin GMAIL API (funcționează pe Render!)
            print(f"📧 Getting Gmail API service...", flush=True)
            service = get_gmail_service()
            if not service:
                print(f"❌ Failed to get Gmail service", flush=True)
                return
            
            print(f"📧 Encoding message...", flush=True)
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            
            print(f"📧 Sending confirmation email via Gmail API...", flush=True)
            service.users().messages().send(userId='me', body=send_message).execute()
            print(f"✅ Email de confirmare trimis către {to_email} (via Gmail API, from {DISPLAY_EMAIL})", flush=True)
        except Exception as e:
            print(f"❌ Confirmation email error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching confirmation email thread...", flush=True)
    thread = threading.Thread(target=send, daemon=True)
    thread.start()
    print(f"🔄 Confirmation email thread started", flush=True)
    return thread

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
        
        # GĂSEȘTE DATELE INVITATULUI DIN SHEET
        print(f"📧 Getting guest info from sheet...", flush=True)
        guest_email = get_email_from_sheet(token)
        guest_name = get_name_from_sheet(token)
        print(f"📧 Found: {guest_name} ({guest_email})", flush=True)
        
        # 1. UPDATE GOOGLE SHEET ÎN BACKGROUND
        print(f"📊 Starting Sheet update thread...", flush=True)
        sheet_thread = update_sheet_background(token, 'da', persoane)
        
        # 2. TRIMITE EMAIL DE CONFIRMARE CĂTRE INVITAT (via Gmail, afișat ca evenimente@unbr.ro)
        print(f"📧 Sending confirmation email to guest...", flush=True)
        guest_email_thread = send_confirmation_email_to_guest(guest_email, guest_name, persoane)
        
        # 3. TRIMITE NOTIFICARE CĂTRE evenimente@unbr.ro (DUBLĂ VERIFICARE)
        print(f"📧 Sending notification to admin...", flush=True)
        admin_email_thread = send_notification_to_admin(
            guest_name,
            guest_email,
            persoane,
            'confirmare'
        )
        
        # AȘTEAPTĂ ca thread-urile să se execute (5 secunde)
        import time
        time.sleep(5)
        print(f"⏰ Threads had 5 seconds to execute", flush=True)
        
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
<p style="margin-top: 20px; font-size: 14px; color: #999;">Veți primi un email de confirmare în curând la {{ email }}.</p>
</div></body></html>
        """, persoane=persoane, email=guest_email)
    
    else:
        # UPDATE GOOGLE SHEET ÎN BACKGROUND
        sheet_thread = update_sheet_background(token, 'nu', None)
        
        # GĂSEȘTE DATELE INVITATULUI DIN SHEET
        guest_email = get_email_from_sheet(token)
        guest_name = get_name_from_sheet(token)
        
        # TRIMITE NOTIFICARE CĂTRE evenimente@unbr.ro
        email_thread = send_notification_to_admin(
            guest_name,
            guest_email,
            '0',
            'declinare'
        )
        
        # AȘTEAPTĂ ca thread-urile să se execute (5 secunde)
        import time
        time.sleep(5)
        print(f"⏰ Threads had 5 seconds to execute", flush=True)
        
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
