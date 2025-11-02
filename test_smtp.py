"""
Script de testare pentru configurația SMTP UNBR.
"""
from smtp_utils import test_email_connection, send_email_smtp
from email_config import EmailConfig

def test_smtp_setup():
    """Testează configurația SMTP"""
    print("=== TESTARE CONFIGURAȚIE SMTP UNBR ===\n")
    
    # Testează conexiunea
    print("1. Testez conexiunea la serverul SMTP...")
    if test_email_connection():
        print("✓ Conexiunea SMTP funcționează!\n")
        
        # Testează trimiterea unui email de test
        print("2. Testez trimiterea unui email de test...")
        test_html = """
        <html>
        <body>
            <h2>Test Email UNBR</h2>
            <p>Acesta este un email de test pentru verificarea configurației SMTP.</p>
            <p>Dacă primești acest email, configurația funcționează corect!</p>
            <p><strong>Trimis de:</strong> evenimente@unbr.ro</p>
        </body>
        </html>
        """
        
        # Înlocuiește cu adresa ta de email pentru test
        test_email = input("Introdu adresa ta de email pentru testare: ").strip()
        
        if test_email:
            success = send_email_smtp(
                recipient=test_email,
                subject="Test Email UNBR - Configurație SMTP",
                html_content=test_html
            )
            
            if success:
                print("✓ Emailul de test a fost trimis cu succes!")
                print("Verifică inbox-ul pentru a confirma primirea.")
            else:
                print("✗ Eroare la trimiterea emailului de test")
        else:
            print("Nu a fost specificată adresa de email pentru test")
    else:
        print("✗ Eroare la conexiunea SMTP")
        print("\nVerifică:")
        print("- Parola este corectă")
        print("- Autentificarea externă este activată pe cont")
        print("- Setările serverului sunt corecte")

if __name__ == "__main__":
    test_smtp_setup()