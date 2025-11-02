"""
Handler pentru răspunsurile automate de confirmare/declinare Concert 2025
"""
from email_organization import create_confirmation_response_email, save_sent_email_to_folder
from smtp_utils import get_email_config, send_email_smtp
from sheets_utils import update_guest_status
import smtplib
from email.utils import formataddr

def send_confirmation_response(guest_name: str, guest_email: str, response_type: str) -> bool:
    """
    Trimite răspuns automat pentru confirmări/declinări PRIN SMTP evenimente@unbr.ro
    
    Args:
        guest_name: Numele invitatului
        guest_email: Emailul invitatului  
        response_type: "confirmare" sau "declinare"
    
    Returns:
        bool: True dacă emailul a fost trimis cu succes
    """
    try:
        # Folosește SMTP direct cu evenimente@unbr.ro
        from smtp_utils import send_email2_smtp, get_email_config
        config = get_email_config()
        
        if not config or not config.email_password:
            print("Eroare: Nu am putut obține configurația email")
            return False
        
        # Creează emailul de răspuns
        message = create_confirmation_response_email(guest_name, response_type, guest_email)
        
        # Trimite emailul prin SMTP evenimente@unbr.ro
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            if config.smtp_use_tls:
                server.starttls()
            
            server.login(config.email_address, config.email_password)
            server.send_message(message)
        
        print(f"✅ Răspuns {response_type} trimis către {guest_email} prin SMTP {config.smtp_server}")
        
        # NU salvăm în foldere Gmail (folosim SMTP, nu Gmail API)
        # if config.organize_by_folders:
        #     save_sent_email_to_folder(message, config, response_type)
        
        # Actualizează statusul în Google Sheets
        confirmation_status = "yes" if response_type == "confirmare" else "no"
        update_guest_status(guest_email, confirmation=confirmation_status)
        print(f"📊 Google Sheet actualizat pentru {guest_email}: {confirmation_status}")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Eroare de autentificare SMTP: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"Eroare SMTP: {e}")
        return False
    except Exception as e:
        print(f"Eroare la trimiterea răspunsului către {guest_email}: {e}")
        return False

def process_guest_response(token: str, response: str) -> bool:
    """
    Procesează răspunsul unui invitat și trimite confirmare automată
    
    Args:
        token: Token-ul unic al invitatului
        response: "da" sau "nu"
    
    Returns:
        bool: True dacă răspunsul a fost procesat cu succes
    """
    try:
        # Găsește invitatul în Google Sheets folosind token-ul
        from sheets_utils import get_guest_list
        
        guests = get_guest_list()
        guest_found = None
        
        for guest in guests:
            if guest.get('token') == token:
                guest_found = guest
                break
        
        if not guest_found:
            print(f"⚠️  Nu s-a găsit invitatul cu token-ul {token}")
            return False
        
        guest_name = guest_found.get('nume_complet', '')
        guest_email = guest_found.get('email', '')
        
        if not guest_email:
            print("⚠️  Email lipsă pentru invitat")
            return False
        
        # Determină tipul de răspuns
        response_type = "confirmare" if response.lower() in ['da', 'yes'] else "declinare"
        
        print(f"📧 Procesez {response_type} pentru {guest_name} ({guest_email})")
        
        # Trimite răspuns automat
        success = send_confirmation_response(guest_name, guest_email, response_type)
        
        if success:
            print(f"✅ Răspuns automat pentru {response_type} trimis cu succes!")
        else:
            print(f"❌ Eroare la trimiterea răspunsului automat")
        
        return success
        
    except Exception as e:
        print(f"❌ Eroare la procesarea răspunsului: {e}")
        return False

def test_confirmation_system():
    """Testează sistemul de răspunsuri automate"""
    print("🧪 TESTARE SISTEM RĂSPUNSURI AUTOMATE\n")
    
    # Date de test
    test_guest_name = "Test User"
    test_guest_email = input("Introdu emailul pentru test: ").strip()
    
    if not test_guest_email:
        print("❌ Email necesar pentru test")
        return
    
    print(f"\n📧 Testez trimiterea răspunsurilor către {test_guest_email}...")
    
    # Test confirmare
    print("\n1️⃣ Testez răspuns de confirmare...")
    if send_confirmation_response(test_guest_name, test_guest_email, "confirmare"):
        print("✅ Răspuns confirmare trimis!")
    else:
        print("❌ Eroare la răspuns confirmare")
    
    # Test declinare  
    print("\n2️⃣ Testez răspuns de declinare...")
    if send_confirmation_response(test_guest_name, test_guest_email, "declinare"):
        print("✅ Răspuns declinare trimis!")
    else:
        print("❌ Eroare la răspuns declinare")
    
    print("\n✅ Test finalizat! Verifică emailurile primite.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_confirmation_system()
    else:
        print("Folosire:")
        print("  python confirmation_system.py test  # Pentru testare")
        print("  Sau importă funcțiile în alte scripturi")