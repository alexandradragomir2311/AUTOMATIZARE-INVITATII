from sheets_utils import get_guest_list

def test_sheet_reading():
    print("Testare citire date din sheet...")
    guests = get_guest_list()
    print(f"\nNumăr total invitați: {len(guests)}")
    
    for guest in guests[:2]:
        print("\nInvitat:")
        print(f"Nume Complet: {guest['nume_complet']}")
        print(f"Instituție: {guest['institutie']}")
        print(f"Funcție: {guest['functie']}")
        print(f"Email: {guest['email']}")
        print(f"Status Email: {guest['email_trimis']}")
        print("\nText Invitație:")
        print(guest['invitation_text'][:200] + "..." if guest['invitation_text'] else "Nu s-a găsit textul invitației")

if __name__ == "__main__":
    test_sheet_reading()