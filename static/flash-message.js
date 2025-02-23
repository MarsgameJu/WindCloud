document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        document.querySelectorAll(".flashes .alert").forEach(alert => {
            alert.style.transition = "opacity 0.5s";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);
});

function flashMessage(message, category) {
    removeFlashMessages();

    const flashContainer = document.querySelector(".flashes");
    if (!flashContainer) return;

    const flashDiv = document.createElement("div");
    flashDiv.className = `alert alert-${category}`;
    flashDiv.textContent = message;
    flashContainer.appendChild(flashDiv);

    setTimeout(() => {
        flashDiv.style.transition = "opacity 0.5s";
        flashDiv.style.opacity = "0";
        setTimeout(() => flashDiv.remove(), 500);
    }, 3000);
}

function removeFlashMessages() {
    document.querySelectorAll(".flashes .alert").forEach(alert => alert.remove());
}

window.flashMessage = flashMessage;  // Macht flashMessage global verfügbar
