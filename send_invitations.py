from sheets_utils import get_guest_list
from smtp_utils import send_email2_smtp

def send_invitations():
    """Send invitations to all guests who haven't received them yet"""
    print("\n=== Starting Invitation Sending Process ===\n")
    guests = get_guest_list()
    print(f"Found {len(guests)} guests in total")
    
    # Count unsent invitations
    unsent = [g for g in guests if not g['email_trimis']]
    print(f"Found {len(unsent)} guests without sent invitations\n")
    
    for guest in unsent:
        print(f"Processing: {guest['nume_complet']} ({guest['email']})")
        if send_email2_smtp(guest):
            print("✓ Invitation sent successfully")
        else:
            print("✗ Failed to send invitation")
        print("-" * 50)
    
    print("\n=== Invitation Sending Process Completed ===")

if __name__ == "__main__":
    send_invitations()
    