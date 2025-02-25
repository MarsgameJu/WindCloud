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
        flashMessage('Passwords do not match!', 'danger');
        console.log('Passwords do not match!');
        return; // Verhindert das Absenden des Formulars
    }

    if (!lengthCriteria || !numberOrSpecialCharCriteria || !caseCriteria) {
        flashMessage('Password does not meet all requirements!', 'danger');
        console.log('Password does not meet all requirements!');
        return; // Verhindert das Absenden des Formulars
    }

    // Wenn alle Bedingungen erfüllt sind, das Formular absenden (kann nach erfolgreicher Validierung gemacht werden)
    flashMessage('Passwords are valid!', 'success');
    console.log('Passwords are valid!');
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
        this.setCustomValidity("Passwords do not match!"); // Fehlermeldung
        flashMessage('Passwords do not match!', 'warning');
        console.log('Passwords do not match!');
    }

    if (password === confirmPassword && password.length >= 8) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
});
