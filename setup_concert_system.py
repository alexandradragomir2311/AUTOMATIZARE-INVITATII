"""
Script pentru configurarea sistemului de organizare a emailurilor Concert 2025
"""
from email_organization import setup_concert_email_system
from smtp_utils import test_email_connection

def main():
    """Configurează sistemul complet de emailuri pentru Concert 2025"""
    print("🎼 CONFIGURARE SISTEM EMAIL CONCERT 2025 🎼\n")
    
    # Testează conexiunea
    print("1️⃣ Testez conexiunea SMTP...")
    if not test_email_connection():
        print("❌ Nu pot continua fără conexiune SMTP")
        return False
    
    # Configurează sistemul de organizare
    print("\n2️⃣ Configurez sistemul de organizare a emailurilor...")
    if setup_concert_email_system():
        print("\n✅ SISTEMUL A FOST CONFIGURAT CU SUCCES!")
        print("\n📋 Rezumat configurare:")
        print("├── 📧 Server SMTP: mail.unbr.ro:587")
        print("├── 📨 Expeditor: evenimente@unbr.ro") 
        print("├── 📁 Folder principal: 'Invitatii Concert 2025'")
        print("└── 📂 Organizare automată: activată")
        
        print("\n🎯 Tipuri de emailuri organizate:")
        print("├── 📮 Invitații → marcate cu 'invitatie'")
        print("├── 🎫 Bilete → marcate cu 'bilet'")
        print("└── ✅ Confirmări → marcate cu 'confirmare'")
        
        print("\n🚀 Poți acum să folosești:")
        print("├── python send_invitations.py (pentru invitații)")
        print("├── python main.py (pentru bilete)")
        print("└── Toate emailurile se vor salva automat în foldere!")
        
        return True
    else:
        print("\n❌ EROARE LA CONFIGURARE")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Configurare întreruptă de utilizator")
    except Exception as e:
        print(f"\n❌ Eroare neașteptată: {e}")