document.addEventListener('DOMContentLoaded', () => {
    const chatWidget = document.getElementById('chat-widget');
    const chatSuggestions = document.getElementById('chat-suggestions');
    const toggleBtn = document.getElementById('chat-toggle-btn');
    const closeBtn = document.getElementById('chat-close-btn');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');
    const sendBtn = document.getElementById('chat-send-btn');
    const clearBtn = document.getElementById('chat-clear-btn');

    const USER_ID_VALUE = window.USER_ID || null;
    let isFirstOpen = true;

    function toggleChatWidget(forceOpen = false) {
        const isOpen = chatWidget.style.display !== 'none';
        if (forceOpen || !isOpen) {
            chatWidget.style.display = 'flex';
            chatWidget.style.pointerEvents = 'auto'; // ✅ thêm dòng này!
    
            if (isFirstOpen) {
                chatSuggestions.style.display = 'flex';
                isFirstOpen = false;
            } else {
                chatSuggestions.style.display = 'none';
            }
    
            setTimeout(() => {
                chatWidget.style.opacity = 1;
                chatWidget.style.transform = 'translateY(0)';
            }, 10);
        } else {
            chatWidget.style.opacity = 0;
            chatWidget.style.transform = 'translateY(20px)';
            chatWidget.style.pointerEvents = 'none'; // ✅ thêm dòng này!
            chatSuggestions.style.display = 'none';
    
            setTimeout(() => {
                chatWidget.style.display = 'none';
            }, 300);
        }
    }
    

    function clearChatHistory() {
        chatBody.innerHTML = '';
        chatBody.scrollTop = 0;
    }

    function appendMessage(content, sender = 'user', isMarkdown = false) {
        const msgWrapper = document.createElement('div');
        msgWrapper.className = `chat-message ${sender} mb-2 d-flex ${sender === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
    
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
    
        bubble.innerHTML = isMarkdown ? marked.parse(content) : content;
    
        msgWrapper.appendChild(bubble);
        chatBody.appendChild(msgWrapper);
    
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-message bot mb-2 d-flex justify-content-start';

        const bubble = document.createElement('div');
        bubble.className = 'p-2 rounded bg-primary text-white text-start opacity-75 fst-italic';
        bubble.innerText = 'Đang soạn...';

        typingDiv.appendChild(bubble);
        chatBody.appendChild(typingDiv);

        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function hideTyping() {
        const typingEl = document.getElementById('typing-indicator');
        if (typingEl) typingEl.remove();
    }

    function sendChat() {
        const question = chatInput.value.trim();
        if (!question) return;

        appendMessage(question, 'user');
        chatInput.value = '';
        hideSuggestions();

        showTyping();

        fetch('https://tuananhahihi.app.n8n.cloud/webhook/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: question, sessionId: USER_ID_VALUE })
        })
        .then(res => res.text())
        .then(data => {
            hideTyping();
            appendMessage(data || 'Xin lỗi, tôi chưa có câu trả lời.', 'bot', true);
        })
        .catch(err => {
            console.error(err);
            hideTyping();
            appendMessage('⚠️ Lỗi khi kết nối AI Agent.', 'bot');
        });
    }

    function sendSuggestion(text) {
        toggleChatWidget(true);

        setTimeout(() => {
            appendMessage(text, 'user');
            hideSuggestions();
            showTyping();

            fetch('https://tuananhahihi.app.n8n.cloud/webhook/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, sessionId: USER_ID_VALUE })
            })
            .then(res => res.text())
            .then(data => {
                hideTyping();
                appendMessage(data || 'Xin lỗi, tôi chưa có câu trả lời.', 'bot', true);
            })
            .catch(err => {
                console.error(err);
                hideTyping();
                appendMessage('⚠️ Lỗi khi kết nối AI Agent.', 'bot');
            });
        }, 300);
    }

    window.sendSuggestion = sendSuggestion;

    // Events
    toggleBtn.addEventListener('click', () => toggleChatWidget());
    closeBtn.addEventListener('click', () => toggleChatWidget());
    sendBtn.addEventListener('click', sendChat);
    clearBtn.addEventListener('click', clearChatHistory);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChat();
        }
    });

    chatInput.addEventListener('input', () => {
        hideSuggestions();
    });

    function hideSuggestions() {
        chatSuggestions.style.display = 'none';
    }
});
