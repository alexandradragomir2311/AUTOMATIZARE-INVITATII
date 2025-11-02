// Google Apps Script pentru gestionarea confirmărilor de participare
// Acest script trebuie încărcat în Google Apps Script și publicat ca Web App

// CONFIGURAȚIE
const SPREADSHEET_ID = '1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg';
const SHEET_NAME = 'INVITATII SI CONFIRMARI';
const DEADLINE = new Date('2025-11-10T23:59:59'); // Termen limită: 10 noiembrie 2025

/**
 * Funcție de test pentru a autoriza scriptul
 * Rulează această funcție MANUAL din editor pentru a acorda permisiuni
 */
function testAuthorization() {
  // Testează accesul la spreadsheet
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_NAME);
  Logger.log('Spreadsheet access: OK');
  Logger.log('Sheet name: ' + sheet.getName());
  
  // Testează trimiterea de email (comentat pentru a nu trimite email real)
  // MailApp.sendEmail('test@example.com', 'Test', 'Test authorization');
  
  Logger.log('Authorization test completed successfully!');
  return 'Authorization OK - You can now use the Web App';
}

/**
 * Funcția principală care gestionează cererile GET pentru confirmări
 */
function doGet(e) {
  return handleRequest(e);
}

/**
 * Funcția care gestionează cererile POST pentru confirmări
 */
function doPost(e) {
  return handleRequest(e);
}

/**
 * Funcția care procesează atât GET cât și POST
 */
function handleRequest(e) {
  try {
    const token = e.parameter.token;
    const resp = e.parameter.resp; // 'da' sau 'nu'
    const persoane = e.parameter.persoane; // '1' sau '2' (doar pentru resp=da)
    
    // Validare parametri
    if (!token) {
      return createHtmlResponse('error', 'Token lipsă. Vă rugăm să folosiți linkul din email.');
    }
    
    // Verifică dacă termenul limită a expirat
    const now = new Date();
    if (now > DEADLINE) {
      return createHtmlResponse('expired', 'Termenul limită pentru confirmări a expirat (10 noiembrie 2025). Pentru modificări, vă rugăm să contactați organizatorii.');
    }
    
    // FORȚEAZĂ permisiunile folosind Lock Service
    const lock = LockService.getScriptLock();
    try {
      lock.waitLock(30000); // Așteaptă max 30 secunde
    } catch (lockError) {
      Logger.log('Lock timeout: ' + lockError.toString());
    }
    
    // Deschide spreadsheet-ul CU PERMISIUNI EXPLICITE
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = ss.getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      return createHtmlResponse('error', 'Sheet-ul nu a fost găsit.');
    }
    
    // Găsește rândul cu tokenul respectiv
    const data = sheet.getDataRange().getValues();
    let rowIndex = -1;
    let email = '';
    let alreadyConfirmed = false;
    
    for (let i = 1; i < data.length; i++) { // Începe de la 1 pentru a sări peste header
      if (data[i][9] === token) { // Coloana J (index 9) = Token
        rowIndex = i + 1; // +1 pentru indexul real în sheet
        email = data[i][4]; // Coloana E = Email
        // Verifică dacă există deja o confirmare (nu este gol și nu este doar spații)
        const confirmValue = String(data[i][7] || '').trim();
        alreadyConfirmed = confirmValue !== '' && confirmValue !== 'Trimis ✅';
        break;
      }
    }
    
    if (rowIndex === -1) {
      return createHtmlResponse('error', 'Token invalid sau expirat. Vă rugăm să folosiți linkul din email.');
    }
    
    // Verifică dacă a mai fost confirmat înainte
    if (!resp) {
      // Dacă a răspuns deja și termenul a expirat, blochez modificarea
      if (alreadyConfirmed && now > DEADLINE) {
        return createHtmlResponse('already_responded', 'Ați răspuns deja la această invitație. Termenul pentru modificări a expirat (10 noiembrie 2025). Pentru modificări, vă rugăm să contactați organizatorii.');
      }
      // Altfel, permite modificări înainte de deadline
      return createPersonSelectionPage(token, email, alreadyConfirmed);
    }
    
    // Actualizează statusul de participare
    let confirmValue = '';
    let numarPersoane = '';
    
    if (resp === 'da') {
      // Dacă utilizatorul confirmă, verificăm dacă a selectat numărul de persoane
      if (persoane === '1' || persoane === '2') {
        numarPersoane = persoane + (persoane === '1' ? ' persoană' : ' persoane');
        confirmValue = '✔ Da - ' + numarPersoane; // Afișează și numărul de persoane
      } else {
        // Arată pagina de selecție pentru numărul de persoane
        return createPersonSelectionPage(token, email, alreadyConfirmed);
      }
    } else if (resp === 'nu') {
      confirmValue = '❌ Nu';
      numarPersoane = '-';
    } else {
      return createHtmlResponse('error', 'Răspuns invalid. Vă rugăm să folosiți linkul din email.');
    }
    
    // Actualizează coloana H (Confirmare) - cu numărul de persoane inclus
    Logger.log('Updating sheet for response: ' + resp + ', persons: ' + persoane);
    
    try {
      sheet.getRange(rowIndex, 8).setValue(confirmValue); // Coloana H
      Logger.log('Set column H (Confirmare): ' + confirmValue);
    } catch (e) {
      Logger.log('ERROR setting column H: ' + e.toString());
      throw e;
    }
    
    try {
      sheet.getRange(rowIndex, 9).setValue(numarPersoane); // Coloana I
      Logger.log('Set column I (Nr. Persoane): ' + numarPersoane);
    } catch (e) {
      Logger.log('ERROR setting column I: ' + e.toString());
      throw e;
    }
    
    // Adaugă timestamp pentru confirmare
    const timestamp = Utilities.formatDate(new Date(), 'GMT+2', 'dd/MM/yyyy HH:mm');
    try {
      sheet.getRange(rowIndex, 10).setNote('Confirmat la: ' + timestamp); // Coloana J (nota celulei cu token)
      Logger.log('Added timestamp note');
    } catch (e) {
      Logger.log('ERROR adding timestamp note: ' + e.toString());
      // Nu aruncăm eroare aici, e doar o notă
    }
    
    // Formatează celula în funcție de răspuns
    const confirmCell = sheet.getRange(rowIndex, 8);
    if (resp === 'da') {
      Logger.log('Setting green background for DA response');
      try {
        confirmCell.setBackground('#d9ead3'); // Verde deschis
        Logger.log('Background set successfully');
      } catch (e) {
        Logger.log('ERROR setting background: ' + e.toString());
      }
      
      // Modifică coloana H pentru primul rând să specifice Persoana 1
      if (persoane === '2') {
        try {
          sheet.getRange(rowIndex, 8).setValue('✔ Da - Persoana 1/2');
          Logger.log('Updated first person marker for 2 people');
        } catch (e) {
          Logger.log('ERROR updating first person marker: ' + e.toString());
          throw e;
        }
      }
      
      // Flush changes pentru a ne asigura că sunt salvate
      try {
        SpreadsheetApp.flush();
        Logger.log('Flush completed successfully');
      } catch (e) {
        Logger.log('ERROR on flush: ' + e.toString());
      }
      
      // Dacă sunt 2 persoane, adaugă un rând nou pentru persoana a 2-a
      if (persoane === '2') {
        Logger.log('Adding row for person 2');
        
        try {
          // Reîncarcă datele pentru a avea ultimele modificări
          const updatedData = sheet.getRange(rowIndex, 1, 1, 10).getValues()[0];
          Logger.log('Loaded data for duplication');
          
          // Inserează un rând nou după rândul curent
          sheet.insertRowAfter(rowIndex);
          const newRowIndex = rowIndex + 1;
          Logger.log('Inserted new row at index: ' + newRowIndex);
          
          // Copiază toate datele în noul rând
          for (let col = 1; col <= 10; col++) {
            sheet.getRange(newRowIndex, col).setValue(updatedData[col - 1]);
          }
          Logger.log('Copied data to new row');
          
          // Modifică coloana H pentru a indica "Persoana 2"
          sheet.getRange(newRowIndex, 8).setValue('✔ Da - Persoana 2/2');
          sheet.getRange(newRowIndex, 8).setBackground('#d9ead3');
          
          // Modifică coloana I
          sheet.getRange(newRowIndex, 9).setValue('Persoana 2');
          
          // Generează un token nou unic pentru persoana a 2-a
          const newToken = Utilities.getUuid().substring(0, 32);
          sheet.getRange(newRowIndex, 10).setValue(newToken);
          sheet.getRange(newRowIndex, 10).setNote('Persoana 2 - Confirmat la: ' + timestamp);
          
          Logger.log('Added row for person 2 with new token: ' + newToken);
          
          // Flush final pentru a salva toate modificările
          SpreadsheetApp.flush();
          Logger.log('Final flush completed for person 2');
        } catch (e) {
          Logger.log('ERROR adding second person row: ' + e.toString());
          // Nu aruncăm eroare - prima persoană a fost deja salvată
        }
      }
    } else {
      Logger.log('Setting red background for NU response');
      try {
        confirmCell.setBackground('#f4cccc'); // Roșu deschis
        SpreadsheetApp.flush();
        Logger.log('Background and flush completed for NU response');
      } catch (e) {
        Logger.log('ERROR setting background for NU: ' + e.toString());
      }
    }
    
    Logger.log('Sheet update completed successfully');
    
    // EMAIL DEZACTIVAT - se trimite prin sistemul SMTP UNBR (evenimente@unbr.ro)
    // Serverul Flask local (confirm_server.py) gestionează trimiterea emailurilor
    Logger.log('Email NOT sent from Google Apps Script - handled by Flask server');
    
    // Returnează pagina de confirmare
    return createHtmlResponse('success', resp, persoane, data[rowIndex - 1][0], alreadyConfirmed); // data[rowIndex - 1][0] = Nume complet
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    return createHtmlResponse('error', 'A apărut o eroare la procesarea cererii. Vă rugăm să contactați organizatorii.');
  } finally {
    // Eliberează lock-ul
    try {
      LockService.getScriptLock().releaseLock();
    } catch (e) {
      Logger.log('Lock release: ' + e.toString());
    }
  }
}

/**
 * Creează pagina de selecție pentru numărul de persoane
 */
function createPersonSelectionPage(token, email, alreadyConfirmed) {
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Confirmați participarea</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 20px;
        }
        
        .container {
          background: white;
          border-radius: 20px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.3);
          max-width: 500px;
          width: 100%;
          padding: 40px;
          text-align: center;
        }
        
        .logo {
          width: 100px;
          height: 100px;
          margin: 0 auto 20px;
          background: #667eea;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 48px;
        }
        
        h1 {
          color: #333;
          margin-bottom: 10px;
          font-size: 28px;
        }
        
        .subtitle {
          color: #666;
          margin-bottom: 20px;
          font-size: 16px;
          line-height: 1.5;
        }
        
        .deadline {
          background: #e3f2fd;
          color: #1976d2;
          padding: 10px 20px;
          border-radius: 8px;
          margin-bottom: 20px;
          font-size: 14px;
          font-weight: 600;
        }
        
        .question {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 10px;
          margin-bottom: 30px;
          font-size: 18px;
          color: #333;
          font-weight: 500;
        }
        
        .buttons {
          display: flex;
          gap: 15px;
          margin-top: 20px;
        }
        
        .btn {
          flex: 1;
          padding: 15px 30px;
          border: none;
          border-radius: 10px;
          font-size: 18px;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
          text-decoration: none;
          display: inline-block;
          color: white;
        }
        
        .btn-1 {
          background: #4CAF50;
        }
        
        .btn-1:hover {
          background: #45a049;
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        .btn-2 {
          background: #2196F3;
        }
        
        .btn-2:hover {
          background: #0b7dda;
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
        }
        
        @media (max-width: 480px) {
          .container {
            padding: 30px 20px;
          }
          
          h1 {
            font-size: 24px;
          }
          
          .buttons {
            flex-direction: column;
          }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="logo">🎵</div>
        <h1>Confirmați participarea</h1>
        <p class="subtitle">Concert omagial UNBR<br>24 noiembrie 2025, ora 19:30<br>Ateneul Român</p>
        <div class="deadline">⏰ Termen limită: 10 noiembrie 2025</div>
        <div class="question">
          Pentru câte persoane doriți să rezervăm locuri?
        </div>
        
        <div class="buttons">
          <form method="POST" action="" style="flex: 1; margin: 0;">
            <input type="hidden" name="token" value="${token}">
            <input type="hidden" name="resp" value="da">
            <input type="hidden" name="persoane" value="1">
            <button type="submit" class="btn btn-1">
              1 persoană
            </button>
          </form>
          <form method="POST" action="" style="flex: 1; margin: 0;">
            <input type="hidden" name="token" value="${token}">
            <input type="hidden" name="resp" value="da">
            <input type="hidden" name="persoane" value="2">
            <button type="submit" class="btn btn-2">
              2 persoane
            </button>
          </form>
        </div>
        
        <p style="margin-top: 30px; font-size: 14px; color: #666; font-style: italic;">
          💡 Puteți răspunde și modifica alegerea până la data de 10 noiembrie 2025
        </p>
      </div>
    </body>
    </html>
  `;
  
  return HtmlService.createHtmlOutput(html)
    .setTitle('Confirmați participarea')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Creează răspunsul HTML pentru utilizator
 */
function createHtmlResponse(type, response, persoane, nume, alreadyConfirmed) {
  let title, icon, message, color;
  
  if (type === 'error') {
    title = 'Eroare';
    icon = '⚠️';
    message = response;
    color = '#f44336';
  } else if (type === 'expired') {
    title = 'Termen expirat';
    icon = '⏰';
    message = response;
    color = '#ff9800';
  } else if (type === 'already_responded') {
    title = 'Răspuns înregistrat';
    icon = '✅';
    message = `
      <p style="font-size: 18px; margin-bottom: 20px;">${response}</p>
      <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <p style="font-size: 16px; margin-bottom: 10px;"><strong>📧 Email:</strong> alexandradragomir23@yahoo.com</p>
        <p style="font-size: 16px; margin-bottom: 10px;"><strong>📞 Telefon:</strong> +40 740 318 791</p>
        <p style="font-size: 16px;"><strong>👤 Contact:</strong> Alexandra-Nicoleta DRAGOMIR</p>
      </div>
    `;
    color = '#2196F3';
  } else if (response === 'da') {
    title = alreadyConfirmed ? 'Participare actualizată!' : 'Participare confirmată!';
    icon = '✅';
    const nrPersoane = persoane === '1' ? '1 persoană' : '2 persoane';
    const updateText = alreadyConfirmed ? 
      '<p style="background: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 15px; color: #2e7d32;">Răspunsul dumneavoastră a fost actualizat cu succes.</p>' : '';
    message = `
      <p style="font-size: 18px; margin-bottom: 20px;">Vă mulțumim pentru confirmare${nume ? ', ' + nume.split(' ')[0] : ''}!</p>
      ${updateText}
      <p style="font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
        Am înregistrat participarea dumneavoastră pentru <strong>${nrPersoane}</strong> la concertul omagial UNBR.
      </p>
      <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <p style="font-size: 16px; margin-bottom: 10px;"><strong>📅 Data:</strong> 24 noiembrie 2025</p>
        <p style="font-size: 16px; margin-bottom: 10px;"><strong>🕐 Ora:</strong> 19:30</p>
        <p style="font-size: 16px;"><strong>📍 Locație:</strong> Ateneul Român, București</p>
      </div>
      <p style="font-size: 16px; line-height: 1.6; color: #666;">
        Veți primi în curând biletul de intrare pe email. Pentru orice întrebări, nu ezitați să ne contactați.
      </p>
      <p style="font-size: 14px; line-height: 1.6; color: #999; margin-top: 20px; font-style: italic;">
        💡 Puteți modifica răspunsul folosind același link din email până la 10 noiembrie 2025.
      </p>
    `;
    color = '#4CAF50';
  } else if (response === 'nu') {
    title = alreadyConfirmed ? 'Răspuns actualizat' : 'Răspuns înregistrat';
    icon = '📝';
    const updateText = alreadyConfirmed ? 
      '<p style="background: #fff3e0; padding: 10px; border-radius: 5px; margin-bottom: 15px; color: #e65100;">Răspunsul dumneavoastră a fost actualizat.</p>' : '';
    message = `
      <p style="font-size: 18px; margin-bottom: 20px;">Vă mulțumim pentru răspuns${nume ? ', ' + nume.split(' ')[0] : ''}!</p>
      ${updateText}
      <p style="font-size: 16px; line-height: 1.6; color: #666;">
        Ne pare rău că nu puteți participa la acest eveniment. Am înregistrat răspunsul dumneavoastră.
      </p>
      <p style="font-size: 16px; line-height: 1.6; color: #666; margin-top: 15px;">
        Sperăm să vă revedem la următoarele evenimente UNBR!
      </p>
      <p style="font-size: 14px; line-height: 1.6; color: #999; margin-top: 20px; font-style: italic;">
        💡 Dacă vă răzgândiți, puteți modifica răspunsul folosind același link din email până la 10 noiembrie 2025.
      </p>
    `;
    color = '#2196F3';
  }
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${title}</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 20px;
        }
        
        .container {
          background: white;
          border-radius: 20px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.3);
          max-width: 600px;
          width: 100%;
          padding: 50px;
          text-align: center;
        }
        
        .icon {
          font-size: 80px;
          margin-bottom: 20px;
          animation: bounce 1s ease;
        }
        
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-20px);
          }
          60% {
            transform: translateY(-10px);
          }
        }
        
        h1 {
          color: ${color};
          margin-bottom: 30px;
          font-size: 32px;
        }
        
        .message {
          color: #333;
          text-align: left;
          line-height: 1.8;
        }
        
        .footer {
          margin-top: 40px;
          padding-top: 30px;
          border-top: 2px solid #f0f0f0;
          color: #666;
          font-size: 14px;
        }
        
        .contact {
          margin-top: 15px;
          font-size: 14px;
          color: #666;
        }
        
        strong {
          color: ${color};
        }
        
        @media (max-width: 480px) {
          .container {
            padding: 30px 20px;
          }
          
          h1 {
            font-size: 24px;
          }
          
          .icon {
            font-size: 60px;
          }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">${icon}</div>
        <h1>${title}</h1>
        <div class="message">
          ${message}
        </div>
        <div class="footer">
          <strong>Uniunea Națională a Barourilor din România</strong>
          <div class="contact">
            📧 Contact: Alexandra-Nicoleta DRAGOMIR<br>
            📞 Tel: +40 21 313 4875 | Mobil: +40 740 318 791<br>
            📍 București, Palatul de Justiție, Splaiul Independenței nr. 5
          </div>
        </div>
      </div>
    </body>
    </html>
  `;
  
  return HtmlService.createHtmlOutput(html)
    .setTitle(title)
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * FUNCȚIE DEZACTIVATĂ - Emailurile se trimit prin SMTP UNBR (evenimente@unbr.ro)
 * Serverul Flask local (confirm_server.py) gestionează trimiterea emailurilor de confirmare
 */
function sendConfirmationEmail(email, response, persoane, nume) {
  Logger.log('sendConfirmationEmail DISABLED - emails handled by Flask SMTP server');
  Logger.log('Email would have been sent to: ' + email + ' (NOT SENT)');
  // MailApp.sendEmail() - DEZACTIVAT
  // Toate emailurile se trimit prin evenimente@unbr.ro via SMTP
}
