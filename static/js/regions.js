function openModal(modalId) {
    const currentModal = document.querySelector('.modal.show'); 
    const modal = document.getElementById(modalId);

    if (currentModal && currentModal !== modal) {
        closeModal(currentModal.id);
    }

    if (!modal) {
        console.warn("Modal não encontrado:", modalId);
        return;
    }

    if (!modal.innerHTML.trim()) {
        fetch(`${modalId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erro ao carregar o conteúdo");
                }
                return response.text();
            })
            .then(html => {
                modal.innerHTML = html;  
                modal.style.display = "flex";
                modal.classList.add("show");
            })
            .catch(error => {
                console.warn("Erro ao carregar a modal:", error);
                modal.innerHTML = "<p>Erro ao carregar o conteúdo.</p>";
                modal.style.display = "flex";
                modal.classList.add("show");
            });
    } else {
        modal.style.display = "flex";
        modal.classList.add("show");
    }
}


function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = "none";
    modal.classList.remove("show");
}

window.onclick = function(event) {
    const modal = event.target;
    if (modal.classList.contains('modal') && modal.classList.contains('show')) {
        closeModal(modal.id);
    }
};

