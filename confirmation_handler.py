from flask import Flask, request, render_template_string, url_for
import base64
import logging
import os
from datetime import datetime
from sheets_utils import update_guest_status
from confirmation_system import send_confirmation_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Termen limită pentru confirmări
DEADLINE = datetime(2025, 11, 10, 23, 59, 59)

# Simplified HTML template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>UNBR - Confirmare</title>
    <style>
        body { 
            font-family: Arial; 
            text-align: center; 
            padding: 50px; 
        }
        .message { 
            color: {{ 'green' if success else 'red' }}; 
            font-size: 24px; 
            margin: 20px; 
        }
    </style>
</head>
<body>
    <div class="message">{{ message }}</div>
</body>
</html>
"""

@app.route('/confirm/<token>')
def confirm(token):
    """Handle confirmation responses"""
    try:
        # Verifică deadline-ul
        if datetime.now() > DEADLINE:
            logger.warning("Confirmation attempt after deadline")
            return render_template_string(
                TEMPLATE,
                message="Termenul limită pentru confirmări a expirat (10 noiembrie 2025). Pentru modificări, vă rugăm să contactați organizatorii.",
                success=False
            )
        
        # Get parameters
        email = request.args.get('email')
        response = request.args.get('response')
        
        logger.info(f"Received confirmation: email={email}, response={response}")
        
        # Validate parameters
        if not email or not response:
            logger.error("Missing email or response")
            return "Invalid parameters", 400
            
        # Verify token
        expected_token = base64.urlsafe_b64encode(email.encode()).decode()
        if token != expected_token:
            logger.error(f"Invalid token for {email}")
            return "Invalid token", 400
            
        # Update sheet
        success = update_guest_status(email=email, confirmation=response)
        if not success:
            logger.error(f"Failed to update status for {email}")
            return "Failed to update status", 500
        
        # Găsește numele invitatului pentru emailul de confirmare
        try:
            from sheets_utils import get_guest_list
            guests = get_guest_list()
            guest_name = "Invitat"
            
            for guest in guests:
                if guest.get('email') == email:
                    guest_name = guest.get('nume_complet', 'Invitat')
                    break
            
            # Trimite răspuns automat prin SMTP UNBR
            response_type = "confirmare" if response == "yes" else "declinare"
            email_sent = send_confirmation_response(guest_name, email, response_type)
            
            if email_sent:
                logger.info(f"Confirmation email sent to {email}")
            else:
                logger.warning(f"Failed to send confirmation email to {email}")
                
        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            
        # Return confirmation page
        message = "Mulțumim pentru confirmarea participării! Veți primi un email de confirmare." if response == "yes" else "Am înregistrat că nu puteți participa. Veți primi un email de confirmare."
        return render_template_string(TEMPLATE, message=message, success=True)
        
    except Exception as e:
        logger.error(f"Error in confirmation handler: {str(e)}")
        return render_template_string(
            TEMPLATE,
            message="A apărut o eroare. Vă rugăm să încercați din nou.",
            success=False
        )

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server...")
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")