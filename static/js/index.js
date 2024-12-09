function openModal(modalId) {
    const currentModal = document.querySelector('.modal.show');
    const modal = document.getElementById(modalId);

    if (currentModal && currentModal !== modal) {
        closeModal(currentModal.id);
    }

    modal.classList.add('show');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
}

window.addEventListener('dragstart', (e) => {
    e.preventDefault();
});

function goBack() {
    if (document.referrer) {
        window.history.back();
    } else {
        window.location.href = "/";
    }
}