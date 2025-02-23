

---

### **To-Do / Checkliste**

1. **Login-Problem**:
   - [ ] Beim erneuten Einloggen sind Karten verändert (andere Buttons, Layout) – **Datenbankproblem beim Aus- und Einloggen**?
     - Untersuchen, warum Karten beim erneuten Login fehlerhaft angezeigt werden.
   
2. **Fehlermeldungen als Flashnachrichten anzeigen**:
   - [ ] Fehlermeldungen sollten als Flash-Nachrichten (Pop-ups) angezeigt werden.
     - Implementiere Flash-Nachrichtensystem für Fehler.

4. **Zugriff auf Dateien über `/Uploads/Dateiname`**:
   - [ ] Momentan kann man direkt über den Pfad `/Uploads/Dateiname` auf die Datei zugreifen, was nicht gewünscht ist.
     - Restriktiere den direkten Zugriff auf Dateien außerhalb des vorgesehenen Rahmens.

5. **Karten können nicht gelöscht werden**:
   - [ ] **Fehlerbehebung** bei Löschvorgang:
     - Fehler beim Löschen der Karte: 
     ```
			DELETE
			http://127.0.0.1:5000/api/cards/1
			[HTTP/1.1 500 INTERNAL SERVER ERROR 10ms]

			Error deleting card: Error: Failed to delete card
   			 <anonymous> http://127.0.0.1:5000/static/dashboard.js:225
			dashboard.js:228:29
    			<anonym> http://127.0.0.1:5000/static/dashboard.js:228
     ```
     - Untersuche den Grund für den Fehler und behebe das Löschen von Karten.

6. **Image Preview**:
   - [ ] Implementiere eine **Vorschau für Bilder**, bevor sie hochgeladen werden.
   
8. **Löschen-Button für Bilder**:
   - [ ] Füge einen Löschen-Button für Bilder im Bearbeitungsmodus hinzu.

9. **Im Share Fenster eingabe zu groß**
---

### **Weitere Aufgaben:**

1. **E-Mail-Verifikation**:
   - [ ] E-Mail-Verifikation ohne Code in der E-Mail (Verifikations-Link statt Code).
   
2. **Passwort zurücksetzen per E-Mail**:
   - [ ] Implementiere ein System, um das Passwort per E-Mail zurückzusetzen.

3. **Content Security Policy (CSP) & HSTS**:
   - [ ] Überprüfe und implementiere **Content Security Policy (CSP)** und **HTTP Strict Transport Security (HSTS)** für erhöhte Sicherheit.

4. **Cookies & Sessions**:
   - [ ] Wie werden Cookies und Sessions im System behandelt? **Überprüfung und Verbesserung der Sicherheit**.

1. **Registrierung**:
   - [ ] Überprüfe bei der Registrierung, ob der Benutzername oder die E-Mail bereits verwendet wird. **Flash-Benachrichtigung bei Nutzung eines bestehenden Namens oder E-Mail**.

