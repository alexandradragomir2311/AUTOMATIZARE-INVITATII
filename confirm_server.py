"""
Server Flask pentru confirmări - intermediar între utilizatori și Google Sheets
Rulează acest server și utilizatorii vor accesa linkuri locale (fără Google Apps Script)
"""

from flask import Flask, request, render_template_string
import gspread
from datetime import datetime
import uuid
from sheets_utils import SPREADSHEET_ID, get_credentials
from confirmation_system import send_confirmation_response
import os

SHEET_NAME = 'INVITATII SI CONFIRMARI'

app = Flask(__name__)

# Configurare Google Sheets - FOLOSEȘTE ACELEAȘI CREDENȚIALE CA test_send.py
def get_sheet():
    """Get Google Sheet using OAuth2 credentials (same as test_send.py)"""
    creds = get_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet.worksheet(SHEET_NAME)

DEADLINE = datetime(2025, 11, 10, 23, 59, 59)

# Template HTML pentru selecție persoane
SELECTION_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmați participarea</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
            text-align: center;
        }
        .logo {
            width: 100px;
            height: 100px;
            margin: 0 auto 20px;
            background: #667eea;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 20px; font-size: 16px; line-height: 1.5; }
        .deadline {
            background: #e3f2fd;
            color: #1976d2;
            padding: 10px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            font-weight: 600;
        }
        .question {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-size: 18px;
            color: #333;
            font-weight: 500;
        }
        .buttons { display: flex; gap: 15px; margin-top: 20px; }
        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            color: white;
        }
        .btn-1 { background: #4CAF50; }
        .btn-1:hover { background: #45a049; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4); }
        .btn-2 { background: #2196F3; }
        .btn-2:hover { background: #0b7dda; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4); }
        .btn-no { background: #f44336; }
        .btn-no:hover { background: #da190b; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4); }
        @media (max-width: 480px) {
            .container { padding: 30px 20px; }
            h1 { font-size: 24px; }
            .buttons { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎵</div>
        <h1>Confirmați participarea</h1>
        <p class="subtitle">Concert omagial UNBR<br>24 noiembrie 2025, ora 19:30<br>Ateneul Român</p>
        <div class="deadline">⏰ Termen limită: 10 noiembrie 2025</div>
        <div class="question">Pentru câte persoane doriți să rezervăm locuri?</div>
        <div class="buttons">
            <a href="/confirm?token={{ token }}&resp=da&persoane=1" class="btn btn-1">1 persoană</a>
            <a href="/confirm?token={{ token }}&resp=da&persoane=2" class="btn btn-2">2 persoane</a>
        </div>
        <div class="buttons" style="margin-top: 15px;">
            <a href="/confirm?token={{ token }}&resp=nu" class="btn btn-no">Nu particip</a>
        </div>
        <p style="margin-top: 30px; font-size: 14px; color: #666; font-style: italic;">
            💡 Puteți răspunde și modifica alegerea până la data de 10 noiembrie 2025
        </p>
    </div>
</body>
</html>
"""

# Template HTML pentru confirmare
SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 50px;
            text-align: center;
        }
        .icon {
            font-size: 80px;
            margin-bottom: 20px;
            animation: bounce 1s ease;
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            60% { transform: translateY(-10px); }
        }
        h1 { color: {{ color }}; margin-bottom: 30px; font-size: 32px; }
        .message { color: #333; text-align: left; line-height: 1.8; }
        .footer {
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #f0f0f0;
            color: #666;
            font-size: 14px;
        }
        .contact { margin-top: 15px; font-size: 14px; color: #666; }
        strong { color: {{ color }}; }
        @media (max-width: 480px) {
            .container { padding: 30px 20px; }
            h1 { font-size: 24px; }
            .icon { font-size: 60px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">{{ icon }}</div>
        <h1>{{ title }}</h1>
        <div class="message">{{ message | safe }}</div>
        <div class="footer">
            <strong>Uniunea Națională a Barourilor din România</strong>
            <div class="contact">
                📧 Contact: Alexandra-Nicoleta DRAGOMIR<br>
                📞 Tel: +40 21 313 4875 | Mobil: +40 740 318 791<br>
                📍 București, Palatul de Justiție, Splaiul Independenței nr. 5
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token')
    resp = request.args.get('resp')
    persoane = request.args.get('persoane')
    
    if not token:
        return render_template_string(SUCCESS_PAGE, 
            title='Eroare', 
            icon='⚠️', 
            message='Token lipsă. Vă rugăm să folosiți linkul din email.',
            color='#f44336')
    
    # Verifică deadline
    if datetime.now() > DEADLINE:
        return render_template_string(SUCCESS_PAGE,
            title='Termen expirat',
            icon='⏰',
            message='Termenul limită pentru confirmări a expirat (10 noiembrie 2025). Pentru modificări, vă rugăm să contactați organizatorii.',
            color='#ff9800')
    
    try:
        sheet = get_sheet()
        all_data = sheet.get_all_values()
        
        # Găsește rândul cu tokenul
        row_index = None
        email = None
        nume = None
        gen = None
        
        for i, row in enumerate(all_data[1:], start=2):  # Skip header
            if len(row) > 9 and row[9] == token:  # Coloana J = index 9
                row_index = i
                nume = row[0]  # Coloana A
                gen = row[3]   # Coloana D (Gen) - index 3 nu 1!
                email = row[4]  # Coloana E
                print(f"🔍 Found guest: {nume}, email: {email}, resp: {resp}, persoane: {persoane}")
                break
        
        if not row_index:
            return render_template_string(SUCCESS_PAGE,
                title='Eroare',
                icon='⚠️',
                message='Token invalid sau expirat. Vă rugăm să folosiți linkul din email.',
                color='#f44336')
        
        # Dacă nu are resp, arată pagina de selecție
        if not resp:
            return render_template_string(SELECTION_PAGE, token=token)
        
        # Procesează răspunsul
        if resp == 'da':
            if not persoane or persoane not in ['1', '2']:
                return render_template_string(SELECTION_PAGE, token=token)
            
            nr_pers = f"{persoane} {'persoană' if persoane == '1' else 'persoane'}"
            confirm_value = f"✔ Da - {nr_pers}"
            
            # Verifică dacă există rând duplicat (Persoana 2/2) și șterge-l dacă acum confirmăm doar 1 persoană
            if persoane == '1':
                # row_index este poziția în Sheet (1-based), all_data include header la index 0
                next_row_data_index = row_index  # În all_data, row_index corespunde următorului rând
                if next_row_data_index < len(all_data):
                    next_row = all_data[next_row_data_index]
                    if len(next_row) > 7 and "Persoana 2/2" in str(next_row[7]):
                        # Șterge rândul duplicat
                        sheet.delete_rows(row_index + 1)
            
            # Actualizează sheet
            sheet.update_cell(row_index, 8, confirm_value)  # Coloana H
            sheet.update_cell(row_index, 9, nr_pers)  # Coloana I
            
            # Background verde
            sheet.format(f"H{row_index}", {"backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83}})
            
            # Dacă 2 persoane, verifică dacă există deja rând duplicat sau adaugă unul nou
            if persoane == '2':
                sheet.update_cell(row_index, 8, "✔ Da - Persoana 1/2")
                
                # Verifică dacă există deja rând pentru Persoana 2
                has_person2 = False
                if row_index < len(all_data):
                    next_row = all_data[row_index] if row_index < len(all_data) else None
                    if next_row and len(next_row) > 7 and "Persoana 2/2" in str(next_row[7]):
                        has_person2 = True
                
                if not has_person2:
                    # Inserează rând nou
                    sheet.insert_row([''] * 10, row_index + 1)
                    
                    # Copiază datele
                    for col_idx in range(1, 8):  # A-G
                        val = sheet.cell(row_index, col_idx).value
                        sheet.update_cell(row_index + 1, col_idx, val)
                    
                    # Setează pentru persoana 2 - FOLOSEȘTE ACELAȘI TOKEN!
                    sheet.update_cell(row_index + 1, 8, "✔ Da - Persoana 2/2")
                    sheet.update_cell(row_index + 1, 9, "Persoana 2")
                    sheet.update_cell(row_index + 1, 10, token)  # Același token ca rândul 1
                    sheet.format(f"H{row_index + 1}", {"backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83}})
            
            # Trimite email confirmare prin SMTP UNBR
            try:
                print(f"📧 Attempting to send confirmation email to {email}...")
                result = send_confirmation_response(nume, email, "confirmare")
                if result:
                    print(f"✅ Confirmation email sent successfully to {email}")
                else:
                    print(f"⚠️  Failed to send confirmation email to {email}")
            except Exception as e:
                print(f"❌ Error sending confirmation email: {e}")
                import traceback
                traceback.print_exc()
            
            # Determină titlul pentru mesaj
            if gen:
                gen_lower = gen.lower()
                titlu = 'Doamnă' if 'doamna' in gen_lower or gen_lower == 'f' else 'Domn'
            else:
                titlu = 'Domn'
            
            message = f"""
            <p style="font-size: 18px; margin-bottom: 20px;">Vă mulțumim pentru confirmare, {titlu} {nume}!</p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
                Am înregistrat participarea dumneavoastră pentru <strong>{nr_pers}</strong> la concertul omagial UNBR.
            </p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p style="font-size: 16px; margin-bottom: 10px;"><strong>📅 Data:</strong> 24 noiembrie 2025</p>
                <p style="font-size: 16px; margin-bottom: 10px;"><strong>🕐 Ora:</strong> 19:30</p>
                <p style="font-size: 16px;"><strong>📍 Locație:</strong> Ateneul Român, București</p>
            </div>
            <p style="font-size: 16px; line-height: 1.6; color: #666;">
                Veți primi în curând biletul de intrare pe email.
            </p>
            """
            
            return render_template_string(SUCCESS_PAGE,
                title='Participare confirmată!',
                icon='✅',
                message=message,
                color='#4CAF50')
        
        elif resp == 'nu':
            # Șterge rândul duplicat dacă există (Persoana 2/2)
            # row_index este poziția în Sheet (1-based), all_data include header la index 0
            if row_index < len(all_data):
                # Verifică dacă rândul următor există și este Persoana 2/2
                next_row_data_index = row_index  # În all_data, row_index corespunde următorului rând
                if next_row_data_index < len(all_data):
                    next_row = all_data[next_row_data_index]
                    if len(next_row) > 7 and "Persoana 2/2" in str(next_row[7]):
                        # Șterge rândul duplicat
                        sheet.delete_rows(row_index + 1)
            
            sheet.update_cell(row_index, 8, '❌ Nu')
            sheet.update_cell(row_index, 9, '-')
            sheet.format(f"H{row_index}", {"backgroundColor": {"red": 0.96, "green": 0.80, "blue": 0.80}})
            
            # Trimite email declinare prin SMTP UNBR
            try:
                print(f"📧 Attempting to send decline email to {email}...")
                result = send_confirmation_response(nume, email, "declinare")
                if result:
                    print(f"✅ Decline email sent successfully to {email}")
                else:
                    print(f"⚠️  Failed to send decline email to {email}")
            except Exception as e:
                print(f"❌ Error sending decline email: {e}")
                import traceback
                traceback.print_exc()
            
            # Determină titlul pentru mesaj
            if gen:
                gen_lower = gen.lower()
                titlu = 'Doamnă' if 'doamna' in gen_lower or gen_lower == 'f' else 'Domn'
            else:
                titlu = 'Domn'
            
            message = f"""
            <p style="font-size: 18px; margin-bottom: 20px;">Vă mulțumim pentru răspuns, {titlu} {nume}!</p>
            <p style="font-size: 16px; line-height: 1.6; color: #666;">
                Ne pare rău că nu puteți participa la acest eveniment. Am înregistrat răspunsul dumneavoastră.
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #666; margin-top: 15px;">
                Sperăm să vă revedem la următoarele evenimente UNBR!
            </p>
            """
            
            return render_template_string(SUCCESS_PAGE,
                title='Răspuns înregistrat',
                icon='📝',
                message=message,
                color='#2196F3')
        
    except Exception as e:
        print(f"ERROR: {e}")
        return render_template_string(SUCCESS_PAGE,
            title='Eroare',
            icon='⚠️',
            message=f'A apărut o eroare: {str(e)}',
            color='#f44336')

if __name__ == '__main__':
    print("\n🚀 SERVER PORNIT pe http://localhost:5000")
    print("📧 Linkurile din email vor funcționa când serverul rulează!")
    print("⚠️  IMPORTANT: Lasă serverul pornit pentru ca invitațiile să funcționeze!\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
