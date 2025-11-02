"""
Main entry point for invitation automation.
Procesează invitații confirmați din Sheet1, generează bilete și trimite emailuri.
"""

from smtp_utils import send_invitation_with_ticket
from sheets_utils import (
    get_confirmed_guests_from_sheet1, 
    transfer_to_sheet2_with_ticket,
    mark_as_processed_in_sheet1,
    update_email_sent_status
)
from ticket_generator import process_guest_ticket

def process_confirmed_invitations():
    """
    Workflow principal:
    1. Preia invitații confirmați din Sheet1 (cu loc alocat)
    2. Generează serie unică, QR code și PDF pentru fiecare
    3. Transferă datele în Sheet2
    4. Trimite email cu biletul PDF
    5. Actualizează statusul în ambele sheet-uri
    """
    print("=" * 60)
    print("ÎNCEPE PROCESAREA INVITAȚIILOR CONFIRMATE")
    print("=" * 60)
    
    # Pasul 1: Preia invitații confirmați din Sheet1
    confirmed_guests = get_confirmed_guests_from_sheet1()
    
    if not confirmed_guests:
        print("Nu există invitați confirmați cu locuri alocate în Sheet1.")
        return
    
    print(f"\nGăsiți {len(confirmed_guests)} invitați confirmați pentru procesare.\n")
    
    # Procesează fiecare invitat
    success_count = 0
    fail_count = 0
    
    for idx, guest in enumerate(confirmed_guests, 1):
        print(f"[{idx}/{len(confirmed_guests)}] Procesare: {guest.get('Nume', '')} {guest.get('Prenume', '')}")
        
        try:
            # Pasul 2: Generează serie unică, QR code și PDF bilet
            print(f"  → Generare bilet...")
            serie_unica, qr_code_path, pdf_path = process_guest_ticket(guest)
            print(f"  ✓ Serie: {serie_unica}")
            print(f"  ✓ QR: {qr_code_path}")
            print(f"  ✓ PDF: {pdf_path}")
            
            # Pasul 3: Transferă în Sheet2
            print(f"  → Transfer în Sheet2...")
            if transfer_to_sheet2_with_ticket(guest, serie_unica, qr_code_path):
                print(f"  ✓ Transferat în Sheet2")
                
                # Pasul 4: Trimite email cu biletul PDF
                email = guest.get('Email', '')
                if email:
                    print(f"  → Trimitere email către {email}...")
                    if send_invitation_with_ticket(email, guest, pdf_path):
                        print(f"  ✓ Email trimis cu succes")
                        
                        # Actualizează statusul de email trimis în Sheet2
                        update_email_sent_status(serie_unica, True)
                        
                        # Pasul 5: Marchează ca procesat în Sheet1
                        mark_as_processed_in_sheet1(guest.get('row_number'))
                        
                        success_count += 1
                        print(f"  ✓ SUCCES COMPLET\n")
                    else:
                        print(f"  ✗ Eroare la trimiterea emailului\n")
                        update_email_sent_status(serie_unica, False)
                        fail_count += 1
                else:
                    print(f"  ✗ Email lipsă\n")
                    fail_count += 1
            else:
                print(f"  ✗ Eroare la transferul în Sheet2\n")
                fail_count += 1
                
        except Exception as e:
            print(f"  ✗ EROARE: {e}\n")
            fail_count += 1
    
    # Rezumat final
    print("=" * 60)
    print("PROCESARE FINALIZATĂ")
    print("=" * 60)
    print(f"Succes: {success_count}")
    print(f"Eșec: {fail_count}")
    print(f"Total: {len(confirmed_guests)}")
    print("=" * 60)

def main() -> None:
    """
    Punctul principal de intrare.
    """
    process_confirmed_invitations()

if __name__ == "__main__":
    main()
