const chatDiv = document.getElementById('chat');
const input = document.getElementById('question');
const btn = document.getElementById('send');

function addMessage(sender, text){
    const div = document.createElement('div');
    div.className = sender;
    div.innerHTML = text;
    chatDiv.appendChild(div);
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

// 추천 질문 예시 (실제 서버 답변으로 대체 가능)
function addRecommendations(recs){
    const div = document.createElement('div');
    div.className = 'recommend';
    div.innerHTML = '추천 질문: ' + recs.join(', ');
    chatDiv.appendChild(div);
}

// 질문 전송
async function sendQuestion(){
    const q = input.value.trim();
    if(!q) return;
    addMessage('user', '나: ' + q);
    input.value = '';

    try{
        const res = await fetch('/api/ask', {
            method:'POST',
            headers:{ 'Content-Type':'application/json' },
            body: JSON.stringify({ question:q })
        });
        const data = await res.json();
        let answer = data.answer || data.error || 'AI 응답 생성 중 오류가 발생했습니다.';
        addMessage('ai', 'AI: ' + answer);

        // 추천 질문 예시
        const recs = ['요트는 어떻게 타?', '체조 훈련 루틴 추천해줘', '야구 투수 훈련 알려줘', '아이스하키 포지션 설명해줘'];
        addRecommendations(recs);
    }catch(e){
        addMessage('ai', 'AI: 서버 오류');
    }
}

// 버튼 클릭
btn.addEventListener('click', sendQuestion);
// 엔터 입력
input.addEventListener('keydown', (e)=>{ if(e.key==='Enter') sendQuestion(); });
