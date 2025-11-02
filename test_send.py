from sheets_utils import get_guest_list, get_pdf_invitation
from smtp_utils import send_email2_smtp
import logging
import sys
import os
import colorama
from colorama import Fore, Style
from googleapiclient.discovery import build
from sheets_utils import get_credentials
import time
import datetime

# Initialize colorama for Windows
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('invitation_logs.txt', 'w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def print_status(message, status="info"):
    """Print colored status messages"""
    timestamp = time.strftime("%H:%M:%S")
    if status == "success":
        print(f"[{timestamp}] {Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    elif status == "error":
        print(f"[{timestamp}] {Fore.RED}✗ {message}{Style.RESET_ALL}")
    elif status == "warning":
        print(f"[{timestamp}] {Fore.YELLOW}! {message}{Style.RESET_ALL}")
    else:
        print(f"[{timestamp}] {Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

def verify_pdf_exists(guest_name: str) -> tuple[bool, str]:
    """Verify PDF exists in Drive and show available PDFs if not found"""
    try:
        print_status("Getting Drive API credentials...")
        creds = get_credentials()
        
        print_status("Connecting to Drive API...")
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Test Drive API access first
        try:
            print_status("Testing Drive API access...")
            drive_service.about().get(fields="user").execute()
        except Exception as api_error:
            print_status("Drive API is not enabled!", "error")
            print_status("Please follow these steps:", "warning")
            print_status("1. Visit this URL:", "info")
            print_status("   https://console.cloud.google.com/apis/library/drive.googleapis.com", "info")
            print_status("2. Click 'Enable API'", "info")
            print_status("3. Wait 2-3 minutes", "info")
            print_status("4. Run this script again", "info")
            return False, None
        
        # Split name into parts
        name_parts = guest_name.split()
        if len(name_parts) >= 2:
            # Create variants for each name part with different character combinations
            def generate_name_variants(name: str) -> list:
                variants = [name]
                char_variants = {
                    'T': ['T', 'Ț', 'Ţ'],
                    'A': ['A', 'Ă', 'Â'],
                    'S': ['S', 'Ș', 'Ş'],
                    'I': ['I', 'Î'],
                }
                
                for char, replacements in char_variants.items():
                    new_variants = []
                    for variant in variants:
                        if char in variant.upper():
                            for replacement in replacements:
                                new_variants.append(variant.replace(char, replacement))
                    variants.extend(new_variants)
                return list(set(variants))  # Remove duplicates
            
            # Generate variants for both name formats
            name_format1 = f"INVITATIE_{guest_name.upper()}"
            name_format2 = f"INVITATIE_{' '.join(reversed(name_parts)).upper()}"
            
            # Replace spaces with underscores
            name_format1 = name_format1.replace(' ', '_')
            name_format2 = name_format2.replace(' ', '_')
            
            # Generate all possible variants
            pdf_names = []
            for fmt in [name_format1, name_format2]:
                variants = generate_name_variants(fmt)
                pdf_names.extend([f"{v}.PDF" for v in variants])
            
            print_status(f"Searching for PDF with {len(pdf_names)} possible name variants")
            print_status(f"Sample variants: {pdf_names[:2]}...")
            
            # Search for all name variants
            query = " or ".join([f"name = '{name}'" for name in pdf_names])
            results = drive_service.files().list(
                q=f"({query}) and mimeType='application/pdf'",
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            items = results.get('files', [])
            
            if items:
                found_filename = items[0]['name']
                print_status(f"Found PDF: {found_filename}", "success")
                return True, found_filename
                
            # If not found, show all PDFs
            print_status(f"PDF not found with any name variant", "warning")
        else:
            print_status(f"Invalid name format: {guest_name}", "error")
            return False, None
        
        # List available PDFs if not found
        all_pdfs = drive_service.files().list(
            q="mimeType='application/pdf'",
            spaces='drive',
            fields='files(name)',
            pageSize=10
        ).execute()
        
        available_pdfs = all_pdfs.get('files', [])
        if available_pdfs:
            print_status("Available PDFs in Drive:", "info")
            for pdf in available_pdfs:
                print(f"  - {pdf['name']}")
        else:
            print_status("No PDFs found in Drive", "warning")
        return False, None
        
    except Exception as e:
        print_status(f"Error checking PDFs: {str(e)}", "error")
        logging.error("PDF check error:", exc_info=True)
        return False, None

def test_send_invitations(force_send=True):
    """Test sending invitations to guests"""
    print_status("=== Starting Invitation Process ===")
    print_status("Checking environment...")
    
    # Check required files
    if not os.path.exists('static/logo.png'):
        print_status("Missing logo file: static/logo.png", "error")
        return
    
    if not os.path.exists('credentials/credentials.json'):
        print_status("Missing credentials file", "error")
        return
    
    try:
        print_status("Getting guest list...")
        guests = get_guest_list()
        print_status(f"Found {len(guests)} guests", "success")
        
        for guest in guests:
            print("\n" + "="*50)
            print_status(f"Processing guest: {guest['nume_complet']}")
            print_status(f"Email: {guest['email']}")
            
            # First verify PDF exists
            exists, filename = verify_pdf_exists(guest['nume_complet'])
            if not exists:
                print_status(f"Skipping {guest['email']} - PDF not found", "warning")
                continue
            
            # Add filename to guest data
            guest['pdf_filename'] = filename
            
            print_status("Attempting to send email...")
            if send_email2_smtp(guest):
                print_status(f"Successfully sent to {guest['email']}", "success")
            else:
                print_status(f"Failed to send to {guest['email']}", "error")
            
            time.sleep(1)  # Slight delay between sends
            
    except Exception as e:
        print_status(f"Critical error: {str(e)}", "error")
        logging.error(f"Stack trace:", exc_info=True)

def wait_until_send_time(target_datetime):
    while True:
        now = datetime.datetime.now()
        if now >= target_datetime:
            break
        seconds_left = (target_datetime - now).total_seconds()
        print_status(f"Aștept până la {target_datetime.strftime('%Y-%m-%d %H:%M')}... ({int(seconds_left)} secunde)")
        time.sleep(min(60, seconds_left))

if __name__ == "__main__":
    try:
        # Test imediat - fără așteptare
        test_send_invitations()
    except KeyboardInterrupt:
        print_status("\nProcess interrupted by user", "warning")
    except Exception as e:
        print_status(f"Fatal error: {str(e)}", "error")
        logging.error("Stack trace:", exc_info=True)
    finally:
        print_status("=== Process Complete ===")
        colorama.deinit()