document.addEventListener('DOMContentLoaded', function () {
    const chatButton = document.querySelector('.chat-button');
    const chatPopup = document.getElementById('chat2');
    const sendButton = document.getElementById('sendButton');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.querySelector('.chat-messages');

    chatButton.addEventListener('click', function () {
        if (chatPopup.style.display === 'none' || chatPopup.style.display === '') {
            chatPopup.style.display = 'block';
        } else {
            chatPopup.style.display = 'none';
        }
    });

    sendButton.addEventListener('click', function () {
        const message = chatInput.value.trim();
        if (message) {
            appendMessage(message, 'user');
            chatInput.value = '';
            showTypingIndicator();
            setTimeout(() => {
                hideTypingIndicator();
                appendMessage("Hi, I am Naphtal USABYUWERA, Can't wait to hear from you! You can leave your message to me me here on Email, usa.naphtal@gmail.com", 'bot');
            }, 1500); // Delay for a more natural response time
        }
    });

    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });

    function appendMessage(message, sender) {
        const messageElement = document.createElement('div');
        const alignmentClass = sender === 'user' ? 'justify-content-end' : 'justify-content-start';
        const bgColor = sender === 'user' ? 'bg-primary text-white' : 'bg-light text-dark';
        const imgSrc = sender === 'user' ? 'https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava4-bg.webp' : 'https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp';

        messageElement.classList.add('d-flex', 'flex-row', alignmentClass, 'mb-4', 'pt-1');
        messageElement.innerHTML = `
            <div>
                <p class="small p-2 me-3 mb-1 rounded-3 ${bgColor}">${message}</p>
                <p class="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">${new Date().toLocaleTimeString()}</p>
            </div>
            <img src="${imgSrc}" alt="avatar" style="width: 45px; height: 100%;">
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.classList.add('d-flex', 'flex-row', 'justify-content-start', 'mb-4', 'pt-1');
        typingElement.setAttribute('id', 'typingIndicator');
        typingElement.innerHTML = `
            <div>
                <p class="small p-2 me-3 mb-1 rounded-3 bg-light text-dark">Typing...</p>
            </div>
            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp" alt="avatar" style="width: 45px; height: 100%;">
        `;
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingElement = document.getElementById('typingIndicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
});
