"""
Modul pentru generarea biletelor PDF cu QR code.
"""
import qrcode
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from typing import Dict
import os

def generate_unique_series() -> str:
    """
    Generează o serie unică pentru bilet (format: EVT-YYYYMMDD-XXXXX).
    """
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"EVT-{date_str}-{unique_id}"

def generate_qr_code(serie_unica: str, guest_data: Dict) -> str:
    """
    Generează un QR code pentru bilet și salvează imaginea.
    Returnează calea către fișierul QR code.
    """
    # Creează datele pentru QR code (JSON sau text simplu)
    qr_data = f"{serie_unica}|{guest_data.get('Nume', '')}|{guest_data.get('Prenume', '')}|{guest_data.get('Loc', '')}"
    
    # Generează QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Creează imaginea QR
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salvează QR code
    qr_folder = "static/qr_codes"
    os.makedirs(qr_folder, exist_ok=True)
    qr_path = os.path.join(qr_folder, f"{serie_unica}.png")
    img.save(qr_path)
    
    return qr_path

def generate_ticket_pdf(guest_data: Dict, serie_unica: str, qr_code_path: str) -> str:
    """
    Generează un bilet PDF personalizat cu QR code.
    Returnează calea către fișierul PDF.
    """
    # Creează folderul pentru bilete
    tickets_folder = "static/tickets"
    os.makedirs(tickets_folder, exist_ok=True)
    
    # Calea PDF-ului
    pdf_path = os.path.join(tickets_folder, f"Bilet_{serie_unica}.pdf")
    
    # Creează PDF-ul
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Titlu
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 50*mm, "INVITAȚIE EVENIMENT")
    
    # Linie decorativă
    c.setStrokeColor(colors.HexColor("#4A90E2"))
    c.setLineWidth(2)
    c.line(50*mm, height - 60*mm, width - 50*mm, height - 60*mm)
    
    # Detalii invitat
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50*mm, height - 80*mm, "Detalii Invitat:")
    
    c.setFont("Helvetica", 14)
    c.drawString(50*mm, height - 95*mm, f"Nume: {guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}")
    c.drawString(50*mm, height - 110*mm, f"Loc alocat: {guest_data.get('Loc', '')}")
    c.drawString(50*mm, height - 125*mm, f"Serie bilet: {serie_unica}")
    
    # QR Code
    if os.path.exists(qr_code_path):
        c.drawImage(qr_code_path, width/2 - 40*mm, height - 200*mm, 
                   width=80*mm, height=80*mm)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, height - 210*mm, "Scanați QR code-ul la intrare")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 30*mm, "Vă așteptăm cu drag!")
    c.drawCentredString(width/2, 20*mm, f"Bilet generat: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    # Salvează PDF-ul
    c.save()
    
    return pdf_path

def process_guest_ticket(guest_data: Dict) -> tuple:
    """
    Procesează complet un invitat: generează serie, QR code și PDF bilet.
    Returnează (serie_unica, qr_code_path, pdf_path).
    """
    # Generează serie unică
    serie_unica = generate_unique_series()
    
    # Generează QR code
    qr_code_path = generate_qr_code(serie_unica, guest_data)
    
    # Generează PDF bilet
    pdf_path = generate_ticket_pdf(guest_data, serie_unica, qr_code_path)
    
    return serie_unica, qr_code_path, pdf_path
