console.log('Sports AI UI Loaded');

// 채팅 메시지 표시
function addMessage(role, text) {
    const chat = document.getElementById('chat');
    const div = document.createElement('div');
    div.className = role === 'user' ? 'msg-user' : 'msg-ai';
    div.innerText = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

// 질문 전송
document.getElementById('input-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const sport = document.getElementById('input-sport').value;
    const q = document.getElementById('question-input').value.trim();

    if (!q) return;

    addMessage('user', q);

    const res = await fetch('/api/ask', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ question:q, sport:sport })
    });

    const data = await res.json();
    addMessage('ai', data.answer);
});
