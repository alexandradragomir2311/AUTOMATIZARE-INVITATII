"""
Configurație pentru deployment pe Render.com
Citește credentialele din environment variables
"""
import os

def get_smtp_credentials():
    """Get SMTP credentials from environment variables"""
    return {
        'smtp_server': os.getenv('SMTP_SERVER', 'mail.unbr.ro'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'smtp_use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
        'email_address': os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro'),
        'email_password': os.getenv('EMAIL_PASSWORD', ''),
    }

def has_smtp_config():
    """Check if SMTP configuration is available"""
    password = os.getenv('EMAIL_PASSWORD', '')
    return bool(password)
