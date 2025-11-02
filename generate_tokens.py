"""
Script pentru generarea token-urilor unice pentru toate înregistrările existente
Rulează acest script o singură dată după actualizarea sistemului
"""

from sheets_utils import get_guest_list
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generează token-uri pentru toate înregistrările"""
    logger.info("=== Generare token-uri unice ===")
    
    try:
        # Această funcție va genera automat token-uri pentru toate înregistrările
        # care nu au deja un token
        guests = get_guest_list()
        
        logger.info(f"Token-uri generate pentru {len(guests)} invitați")
        logger.info("Token-urile au fost salvate în coloana J din Google Sheet")
        
        # Afișează primele 3 token-uri ca exemplu
        if guests:
            logger.info("\nExemple de token-uri generate:")
            for i, guest in enumerate(guests[:3], 1):
                logger.info(f"{i}. {guest['nume_complet']}: {guest['token'][:16]}...")
        
        logger.info("\n✅ Token-urile au fost generate cu succes!")
        logger.info("Acum poți trimite invitațiile folosind python main.py sau python test_send.py")
        
    except Exception as e:
        logger.error(f"Eroare la generarea token-urilor: {e}")
        raise

if __name__ == "__main__":
    main()
