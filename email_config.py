"""
Configurația pentru serverul de email personalizat UNBR.
"""
import os
from dataclasses import dataclass

@dataclass
class EmailConfig:
    """Configurația pentru serverul SMTP UNBR"""
    smtp_server: str = "mail.unbr.ro"
    smtp_port: int = 587  # Folosim 587 cu STARTTLS
    smtp_use_tls: bool = True
    
    # Configurări pentru IMAP (pentru salvarea în Sent și organizarea emailurilor)
    imap_server: str = "mail.unbr.ro"
    imap_port: int = 993
    imap_use_ssl: bool = True
    
    # Configurări pentru POP3 (dacă avem nevoie să citim emailuri)
    pop_server: str = "mail.unbr.ro"
    pop_port: int = 995
    pop_use_ssl: bool = True
    
    # Credentiale - vor fi setate din variabile de mediu sau dintr-un fișier sigur
    email_address: str = "evenimente@unbr.ro"
    email_password: str = ""  # Va fi setat dinamic
    
    # Configurări pentru organizarea emailurilor
    save_sent_emails: bool = False  # NU salvează în Sent, doar în foldere specifice
    organize_by_folders: bool = True  # Organizează în foldere
    concert_folder_name: str = "Invitatii Transmise Concert 2025"  # Folderul pentru invitații trimise
    confirmations_folder_name: str = "Confirmari Concert 2025"  # Folderul pentru confirmări
    
    @classmethod
    def load_from_env(cls):
        """Încarcă configurația din variabilele de mediu"""
        config = cls()
        config.email_password = os.getenv('EMAIL_PASSWORD', '')
        return config
    
    @classmethod
    def load_from_file(cls, credentials_file: str = 'credentials/email_credentials.txt'):
        """Încarcă parola din fișier"""
        config = cls()
        try:
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r', encoding='utf-8') as f:
                    config.email_password = f.read().strip()
        except Exception as e:
            print(f"Eroare la încărcarea credentialelor din fișier: {e}")
        return config