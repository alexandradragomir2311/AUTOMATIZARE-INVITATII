"""
Script helper pentru configurarea sigură a parolei de email UNBR.
"""
import os
import getpass
from pathlib import Path

def setup_email_password():
    """Configurează parola de email în mod sigur"""
    print("=== CONFIGURARE SIGURĂ PAROLĂ EMAIL UNBR ===\n")
    
    credentials_dir = Path("credentials")
    credentials_file = credentials_dir / "email_credentials.txt"
    
    # Verifică dacă directorul există
    if not credentials_dir.exists():
        credentials_dir.mkdir(exist_ok=True)
        print("✓ Directorul 'credentials' a fost creat")
    
    # Verifică dacă parola există deja
    if credentials_file.exists():
        with open(credentials_file, 'r', encoding='utf-8') as f:
            existing_password = f.read().strip()
        
        if existing_password and existing_password != "INTRODU_PAROLA_AICI":
            print("🔒 Există deja o parolă configurată.")
            choice = input("Vrei să o schimbi? (da/nu): ").strip().lower()
            if choice not in ['da', 'd', 'yes', 'y']:
                print("Parola existentă păstrată.")
                return True
    
    print("🔐 Introdu parola pentru contul evenimente@unbr.ro")
    print("IMPORTANT: Parola va fi salvată local în siguranță și NU va fi trimisă pe internet")
    print("(Textul nu va fi vizibil când tastezi - normal pentru parole)\n")
    
    # Folosește getpass pentru introducerea sigură a parolei
    password = getpass.getpass("Parola evenimente@unbr.ro: ")
    
    if not password.strip():
        print("❌ Parola nu poate fi goală!")
        return False
    
    # Confirmă parola
    password_confirm = getpass.getpass("Confirmă parola: ")
    
    if password != password_confirm:
        print("❌ Parolele nu se potrivesc!")
        return False
    
    # Salvează parola
    try:
        with open(credentials_file, 'w', encoding='utf-8') as f:
            f.write(password.strip())
        
        # Setează permisiuni restrictive (doar pentru owner)
        if os.name != 'nt':  # Unix/Linux/Mac
            os.chmod(credentials_file, 0o600)
        
        print(f"✅ Parola a fost salvată în siguranță în: {credentials_file}")
        print("🔒 Fișierul este protejat și nu va fi trimis pe Git")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la salvarea parolei: {e}")
        return False

def test_email_setup():
    """Testează configurația email după setarea parolei"""
    print("\n=== TESTARE CONFIGURAȚIE ===")
    
    try:
        from smtp_utils import test_email_connection
        
        if test_email_connection():
            print("✅ Configurația SMTP funcționează perfect!")
            return True
        else:
            print("❌ Probleme cu configurația SMTP")
            return False
            
    except ImportError as e:
        print(f"❌ Eroare la importul modulelor: {e}")
        return False
    except Exception as e:
        print(f"❌ Eroare neașteptată: {e}")
        return False

def main():
    """Funcția principală"""
    print("🚀 Configurare automată email UNBR\n")
    
    # Configurează parola
    if setup_email_password():
        print("\n" + "="*50)
        
        # Testează configurația
        if test_email_setup():
            print("\n🎉 CONFIGURAREA S-A FINALIZAT CU SUCCES!")
            print("\nPoți acum să folosești:")
            print("  python send_invitations.py  # Pentru trimiterea invitațiilor")
            print("  python test_smtp.py         # Pentru teste suplimentare")
        else:
            print("\n⚠️  Configurarea parolei a reușit, dar există probleme cu conexiunea SMTP")
            print("Verifică:")
            print("  - Parola introdusă este corectă")
            print("  - Autentificarea externă este activată pe cont")
            print("  - Conexiunea la internet funcționează")
    else:
        print("\n❌ Configurarea nu s-a finalizat cu succes")
        print("Încearcă din nou sau contactează administratorul")

if __name__ == "__main__":
    main()