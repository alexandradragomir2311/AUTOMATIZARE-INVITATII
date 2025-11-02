"""
Script rapid pentru a testa linkul de confirmare cu token real
"""
from sheets_utils import get_guest_list

print("Citesc lista de invitați...")
guests = get_guest_list()

if guests:
    # Ia primul invitat
    guest = guests[0]
    token = guest.get('token', '')
    email = guest.get('email', '')
    
    if token:
        test_url = f"https://automatizare-invitatii.onrender.com/confirm?token={token}"
        print(f"\n✅ Token găsit pentru {email}")
        print(f"\n📋 Link de test:")
        print(test_url)
        print(f"\n🔗 Deschide acest link în browser pentru a testa!")
    else:
        print("❌ Nu există token pentru acest invitat")
else:
    print("❌ Nu s-au găsit invitați")
