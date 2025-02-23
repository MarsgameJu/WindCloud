document.getElementById('password-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Verhindert das Absenden des Formulars, damit wir zuerst validieren

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Kriterien für Passwort
    const lengthCriteria = password.length >= 8;
    const numberOrSpecialCharCriteria = /[0-9!@#$%^&*(),.?":{}|<>]/.test(password);
    const caseCriteria = /[a-z]/.test(password) && /[A-Z]/.test(password);

    // Überprüfung der Passwortbedingungen
    if (password !== confirmPassword) {
        flashMessage('Die Passwörter stimmen nicht überein!', 'danger');
        console.log('Die Passwörter stimmen nicht überein!');
        return; // Verhindert das Absenden des Formulars
    }

    if (!lengthCriteria || !numberOrSpecialCharCriteria || !caseCriteria) {
        flashMessage('Das Passwort erfüllt nicht alle Anforderungen!', 'danger');
        console.log('Das Passwort erfüllt nicht alle Anforderungen!');
        return; // Verhindert das Absenden des Formulars
    }

    // Wenn alle Bedingungen erfüllt sind, das Formular absenden (kann nach erfolgreicher Validierung gemacht werden)
    flashMessage('Passwörter sind gültig!', 'success');
    console.log('Passwörter sind gültig!');
    this.submit(); // Formular wird tatsächlich abgeschickt
});


document.getElementById('password').addEventListener('input', function () {
    const password = this.value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const progressBar = document.getElementById('password-progress');
    const requirements = document.querySelectorAll('.requirement input');
    const submitBtn = document.getElementById('submit-btn');

    // Passwortstärke prüfen
    const lengthCriteria = password.length >= 8;
    const numberOrSpecialCharCriteria = /[0-9!@#$%^&*(),.?":{}|<>]/.test(password);
    const caseCriteria = /[a-z]/.test(password) && /[A-Z]/.test(password);

    let fulfilledConditions = 0;
    if (lengthCriteria) fulfilledConditions++;
    if (numberOrSpecialCharCriteria) fulfilledConditions++;
    if (caseCriteria) fulfilledConditions++;

    const strengthPercentage = (fulfilledConditions / 3) * 100;
    progressBar.style.width = `${strengthPercentage}%`;

    if (password.length === 0) {
        progressBar.style.backgroundColor = 'transparent';
    } else if (fulfilledConditions === 1) {
        progressBar.style.backgroundColor = '#ff4c4c';
    } else if (fulfilledConditions === 2) {
        progressBar.style.backgroundColor = '#ffbf00';
    } else if (fulfilledConditions === 3) {
        progressBar.style.backgroundColor = '#4caf50';
    }

    // Anforderungen anzeigen
    requirements[0].checked = lengthCriteria;
    requirements[1].checked = numberOrSpecialCharCriteria;
    requirements[2].checked = caseCriteria;

    // Passwort bestätigen prüfen
    if (password === confirmPassword && lengthCriteria && numberOrSpecialCharCriteria && caseCriteria) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
});

document.getElementById('confirm-password').addEventListener('input', function () {
    const password = document.getElementById('password').value;
    const confirmPassword = this.value;
    const submitBtn = document.getElementById('submit-btn');

    // Passwortbestätigung prüfen
    if (password === confirmPassword) {
        this.setCustomValidity(""); // Keine Fehlermeldung
    } else {
        this.setCustomValidity("Die Passwörter stimmen nicht überein!"); // Fehlermeldung
        flashMessage('Passwörter stimmen nicht überein', 'warning');
        console.log('Passwörter stimmen nicht überein');
    }

    if (password === confirmPassword && password.length >= 8) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
});
