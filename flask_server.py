"""
Flask server for handling confirmation links and guest responses.
"""
from flask import Flask, request, jsonify
from sheets_utils import mark_prezenta
from datetime import datetime

app = Flask(__name__)

@app.route("/confirm", methods=["GET"])
def confirm():
    """
    Endpoint pentru confirmarea prezenței invitatului.
    """
    return jsonify({"status": "success"})

@app.route("/checkin", methods=["POST"])
def checkin():
    """
    Endpoint pentru scanarea QR code și marcarea prezenței.
    Primește: {serie_bilet, nume, prenume}
    """
    data = request.json
    serie = data.get('serie_bilet', '')
    nume = data.get('nume', '')
    prenume = data.get('prenume', '')
    
    ora_sosire = datetime.now().strftime('%H:%M:%S')
    
    if mark_prezenta(nume, prenume, ora_sosire):
        return jsonify({"status": "success", "message": "Prezență înregistrată!"})
    else:
        return jsonify({"status": "error", "message": "Eroare la înregistrarea prezenței"}), 500

if __name__ == "__main__":
    app.run(debug=True)
