document.addEventListener('DOMContentLoaded', function () {
    const chatButton = document.querySelector('.chat-button');
    const chatPopup = document.getElementById('chat2');
    const sendButton = document.getElementById('sendButton');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const charCountElement = document.getElementById('charCount');
    const charCounterElement = document.getElementById('charCounter');

    let isAwaitingResponse = false;
    let messageCount = 0;
    let currentReplyToken = null;
    let replyCheckInterval = null;

    // Initialize chat
    initializeChat();

    function initializeChat() {
        // Add welcome message on first load
        setTimeout(() => {
            addWelcomeMessage();
        }, 500);

        // Setup input handlers
        setupInputHandlers();
    }

    function setupInputHandlers() {
        // Auto-resize textarea
        chatInput.addEventListener('input', function() {
            // Reset height to auto to get the correct scrollHeight
            this.style.height = 'auto';

            // Set new height based on scrollHeight
            const newHeight = Math.min(this.scrollHeight, 120);
            this.style.height = newHeight + 'px';

            // Update character counter
            updateCharacterCounter();
        });

        // Handle mobile keyboard
        if (window.innerWidth <= 768) {
            chatInput.addEventListener('focus', function() {
                setTimeout(() => {
                    scrollToBottom();
                }, 300);
            });
        }
    }

    function updateCharacterCounter() {
        const currentLength = chatInput.value.length;
        const maxLength = 500;

        if (charCountElement && charCounterElement) {
            charCountElement.textContent = currentLength;

            if (currentLength > maxLength * 0.8) {
                charCounterElement.style.display = 'block';
                charCounterElement.style.color = currentLength > maxLength * 0.9 ? '#dc3545' : '#ffc107';
            } else {
                charCounterElement.style.display = 'none';
            }
        }
    }

    function addWelcomeMessage() {
        const welcomeHtml = `
            <div class="welcome-message">
                <span class="emoji">👋</span>
                <p class="mb-1"><strong>Hi there! I'm Naphtal</strong></p>
                <small class="text-muted d-block mb-2">AI Engineer & Full Stack Developer</small>
                <p class="mb-0">Feel free to ask me anything about my work, projects, or just say hello!</p>
            </div>
        `;
        chatMessages.innerHTML = welcomeHtml;
    }

    // Chat button toggle
    if (chatButton) {
        chatButton.addEventListener('click', toggleChat);
    }

    function toggleChat() {
        if (chatPopup.style.display === 'none' || chatPopup.style.display === '') {
            openChat();
        } else {
            closeChat();
        }
    }

    function openChat() {
        chatPopup.style.display = 'block';

        // Focus input after animation
        setTimeout(() => {
            chatInput.focus();
        }, 100);

        // Clear welcome message and add proper greeting if no messages yet
        if (messageCount === 0) {
            chatMessages.innerHTML = '';
            setTimeout(() => {
                appendMessage("👋 Hey there! Great to see you here. What would you like to know about my work or discuss?", 'bot');
            }, 300);
        }

        // Handle mobile viewport
        if (window.innerWidth <= 768) {
            document.body.style.overflow = 'hidden';
            setTimeout(() => {
                scrollToBottom();
            }, 100);
        }
    }

    function closeChat() {
        chatPopup.style.display = 'none';

        // Stop reply checking when chat is closed
        if (replyCheckInterval) {
            clearInterval(replyCheckInterval);
            replyCheckInterval = null;
        }

        // Restore body scroll on mobile
        if (window.innerWidth <= 768) {
            document.body.style.overflow = '';
        }
    }

    // Send message handlers
    sendButton.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    async function handleSendMessage() {
        if (isAwaitingResponse) return;

        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        appendMessage(message, 'user');
        chatInput.value = '';
        chatInput.style.height = 'auto';
        updateCharacterCounter();
        messageCount++;

        // Set loading state
        setLoadingState(true);
        showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    timestamp: new Date().toISOString()
                })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.success) {
                // Add bot response
                appendMessage(data.bot_response, 'bot');

                // Store reply token if provided
                if (data.reply_token) {
                    currentReplyToken = data.reply_token;
                    startReplyChecking();
                }

                // Add follow-up suggestions after first message
                if (messageCount === 1) {
                    setTimeout(() => {
                        appendMessage("💡 You can ask me about:\n• My projects and experience\n• Technical skills\n• Collaboration opportunities\n• You want to Hire me Or anything else!", 'bot');
                    }, 1500);
                }
            } else {
                appendMessage("Sorry, there was an issue. Please try again or email me at usanaphtal112@gmail.com", 'bot');
            }
        } catch (error) {
            console.error('Chat error:', error);
            hideTypingIndicator();
            appendMessage("Connection issue! Please email me directly: usanaphtal112@gmail.com", 'bot');
        } finally {
            setLoadingState(false);
        }
    }

    function startReplyChecking() {
        // Don't start multiple intervals
        if (replyCheckInterval) {
            clearInterval(replyCheckInterval);
        }

        // Check for replies every 5 seconds
        replyCheckInterval = setInterval(async () => {
            if (!currentReplyToken) return;

            try {
                const response = await fetch('/api/chat/check-reply/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        token: currentReplyToken
                    })
                });

                const data = await response.json();

                if (data.has_reply) {
                    appendMessage(data.reply, 'bot', false, false, "✨ <em>This was a direct reply from Naphtal!</em>");
                    // Stop checking for this token
                    currentReplyToken = null;
                    clearInterval(replyCheckInterval);
                    replyCheckInterval = null;
                }
            } catch (error) {
                console.error('Reply check error:', error);
            }
        }, 5000); // Check every 5 seconds

        // Stop checking after 30 minutes to prevent endless polling
        setTimeout(() => {
            if (replyCheckInterval) {
                clearInterval(replyCheckInterval);
                replyCheckInterval = null;
            }
        }, 30 * 60 * 1000); // 30 minutes
    }

    function appendMessage(message, sender, isHtml = false, isSystem = false, replyNotice = null) {
        const messageContainer = document.createElement('div');
        messageContainer.className = isSystem ? 'system-message' : `message-container ${sender}`;

        const isUser = sender === 'user';
        const avatarSrc = isUser
            ? 'https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava4-bg.webp'
            : 'https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp';

        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

        // Format message (handle line breaks or HTML)
        const formattedMessage = isHtml ? message : message.replace(/\n/g, '<br>');

        let noticeHtml = '';
        if (replyNotice) {
            noticeHtml = `<div class="reply-notice">${replyNotice}</div>`;
        }

        messageContainer.innerHTML = `
            ${!isUser ? `<img src="${avatarSrc}" alt="avatar" class="message-avatar">` : ''}
            <div class="message-content">
                <div class="message-bubble">
                    ${formattedMessage}
                </div>
                ${noticeHtml}
                <div class="message-time">${currentTime}</div>
            </div>
            ${isUser ? `<img src="${avatarSrc}" alt="avatar" class="message-avatar">` : ''}
        `;

        chatMessages.appendChild(messageContainer);
        scrollToBottom();

        // Add entrance animation
        setTimeout(() => {
            messageContainer.style.opacity = '1';
            messageContainer.style.transform = 'translateY(0)';
        }, 10);
    }

    function showTypingIndicator() {
        const typingContainer = document.createElement('div');
        typingContainer.className = 'message-container bot';
        typingContainer.id = 'typingIndicator';

        typingContainer.innerHTML = `
            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp"
                 alt="avatar" class="message-avatar">
            <div class="message-content">
                <div class="message-bubble typing-indicator">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span>Naphtal is typing...</span>
                </div>
            </div>
        `;

        chatMessages.appendChild(typingContainer);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const typingElement = document.getElementById('typingIndicator');
        if (typingElement) {
            typingElement.remove();
        }
    }

    function setLoadingState(loading) {
        isAwaitingResponse = loading;
        chatInput.disabled = loading;
        sendButton.disabled = loading;

        if (loading) {
            sendButton.innerHTML = `
                <div class="spinner-border spinner-border-sm" role="status" style="width: 16px; height: 16px;">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `;
        } else {
            sendButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                    <path d="l.5 1.163A1 1 0 0 0 1.97.28l12.868 6.837a1 1 0 0 0 0 1.766L1.969 15.72A1 1 0 0 0 .5 14.836l.713-2.852a.5.5 0 0 0 .02-.183L.5 1.163z"/>
                    <path d="M5.072 8.5 1.539 2.844l.713 2.852a.5.5 0 0 1-.02.183L5.072 8.5z"/>
                </svg>
            `;
        }
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 10);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle window resize
    window.addEventListener('resize', function() {
        if (chatPopup.style.display !== 'none') {
            setTimeout(() => {
                scrollToBottom();
            }, 100);
        }
    });

    // Handle orientation change on mobile
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            if (chatPopup.style.display !== 'none') {
                scrollToBottom();
            }
        }, 500);
    });

    // Close chat when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && chatPopup.style.display !== 'none') {
            if (!chatPopup.contains(e.target) && !chatButton.contains(e.target)) {
                closeChat();
            }
        }
    });

    // Prevent body scroll when chat is open on mobile
    chatPopup.addEventListener('touchmove', function(e) {
        e.stopPropagation();
    });

    // Global function for closing chat from header button
    window.toggleChat = toggleChat;

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape to close chat
        if (e.key === 'Escape' && chatPopup.style.display !== 'none') {
            closeChat();
        }
    });

    // Clean up intervals when page is unloaded
    window.addEventListener('beforeunload', function() {
        if (replyCheckInterval) {
            clearInterval(replyCheckInterval);
        }
    });

});
