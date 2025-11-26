# src/ai/ai_client.py
# OpenAI wrapper + simple summarizer helper
import os
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def ask_openai(prompt: str, model: str = 'gpt-4o', max_tokens: int = 600, temperature: float = 0.6) -> str:
    if not OPENAI_API_KEY:
        return 'OpenAI API key not set. Please add OPENAI_API_KEY to .env'
    try:
        import openai
    except Exception:
        return 'openai 패키지가 설치되어 있지 않습니다. requirements.txt를 확인하세요.'

    openai.api_key = OPENAI_API_KEY

    for attempt in range(3):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert sports coach and concise assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            text = resp['choices'][0]['message']['content'].strip()
            return text
        except Exception as e:
            last_err = str(e)
            time.sleep(1 + attempt * 2)
    return f'OpenAI 요청 실패: {last_err}'

def summarize_text(text: str, max_chars: int = 800) -> str:
    # 간단한 요약을 위해 OpenAI 호출(선택). 여기서는 텍스트가 길면 자름.
    if len(text) <= max_chars:
        return text
    prompt = f\"\"\"다음 내용을 간결하게 한국어로 요약해줘 (최대 {max_chars}자):
---
{text}
\"\"\"
    return ask_openai(prompt)
