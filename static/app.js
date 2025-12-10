const API_URL = 'https://sports-ai-d2wm.onrender.com'; // Render 배포 URL

const messagesDiv = document.getElementById('messages');
const input = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');

function addMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = sender;
    msgDiv.textContent = ${sender}: ;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendQuestion() {
    const question = input.value.trim();
    if (!question) return;
    addMessage('나', question);
    input.value = '';

    try {
        const res = await fetch(${API_URL}/api/ask, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await res.json();
        addMessage('AI', data.answer || "'응답 없음'");
    } catch (err) {
        addMessage('AI', "오류 발생: API 요청 실패");
    }
}

// 전송 버튼 클릭
sendBtn.addEventListener('click', sendQuestion);

// 엔터로 전송
input.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendQuestion();
        e.preventDefault();
    }
});
