document.addEventListener("DOMContentLoaded", function() {
    // Registrierung-spezifische Events nur anhängen, wenn #password vorhanden ist
    if (document.getElementById('password')) {
        document.getElementById('password-form').addEventListener('submit', function(event) {
            event.preventDefault();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const lengthCriteria = password.length >= 8;
            const numberOrSpecialCharCriteria = /[0-9!@#$%^&*(),.?":{}|<>]/.test(password);
            const caseCriteria = /[a-z]/.test(password) && /[A-Z]/.test(password);
            if (password !== confirmPassword) {
                flashMessage('Passwords do not match!', 'danger');
                console.log('Passwords do not match!');
                return;
            }
            if (!lengthCriteria || !numberOrSpecialCharCriteria || !caseCriteria) {
                flashMessage('Password does not meet all requirements!', 'danger');
                console.log('Password does not meet all requirements!');
                return;
            }
            flashMessage('Passwords are valid!', 'success');
            console.log('Passwords are valid!');
            this.submit();
        });

        document.getElementById('password').addEventListener('input', function () {
            const password = this.value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const progressBar = document.getElementById('password-progress');
            const requirements = document.querySelectorAll('.requirement input');
            const submitBtn = document.getElementById('submit-btn');
            const lengthCriteria = password.length >= 8;
            const numberOrSpecialCharCriteria = /[0-9!@#$%^&*(),.?":{}|<>]/.test(password);
            const caseCriteria = /[a-z]/.test(password) && /[A-Z]/.test(password);
            let fulfilledConditions = 0;
            if (lengthCriteria) fulfilledConditions++;
            if (numberOrSpecialCharCriteria) fulfilledConditions++;
            if (caseCriteria) fulfilledConditions++;
            const strengthPercentage = (fulfilledConditions / 3) * 100;
            progressBar.style.width = `${strengthPercentage}%`;
            progressBar.style.backgroundColor = password.length === 0 ? 'transparent' :
                fulfilledConditions === 1 ? '#ff4c4c' :
                fulfilledConditions === 2 ? '#ffbf00' : '#4caf50';
            requirements[0].checked = lengthCriteria;
            requirements[1].checked = numberOrSpecialCharCriteria;
            requirements[2].checked = caseCriteria;
            submitBtn.disabled = !(password === confirmPassword && lengthCriteria && numberOrSpecialCharCriteria && caseCriteria);
        });

        document.getElementById('confirm-password').addEventListener('input', function () {
            const password = document.getElementById('password').value;
            const confirmPassword = this.value;
            const submitBtn = document.getElementById('submit-btn');
            if (password === confirmPassword) {
                this.setCustomValidity("");
            } else {
                this.setCustomValidity("Passwords do not match!");
                flashMessage('Passwords do not match!', 'warning');
                console.log('Passwords do not match!');
            }
            submitBtn.disabled = !(password === confirmPassword && password.length >= 8);
        });
    }

    // Toggle-Passwort (für Registrierung & Login) – beide Seiten haben .toggle-password
    const toggleButtons = document.querySelectorAll(".toggle-password");
    toggleButtons.forEach(function(button) {
        button.addEventListener("click", function() {
            const targetId = button.getAttribute("data-target");
            const passwordField = document.getElementById(targetId);
            if (passwordField) {
                if (passwordField.type === "password") {
                    passwordField.type = "text";
                    button.innerHTML = '<span class="material-icons">visibility_off</span>';
                } else {
                    passwordField.type = "password";
                    button.innerHTML = '<span class="material-icons">visibility</span>';
                }
            }
        });
    });
});
