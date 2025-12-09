# src/ai/ai_client.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def ask_openai(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 500) -> str:
    """
    OpenAI API를 호출해 질문에 대한 답변을 생성
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"OpenAI API 호출 에러: {e}")
        return "AI 응답 생성 중 오류가 발생했습니다."

def summarize_content(content: str, max_chars: int = 200) -> str:
    """
    내용을 간결하게 한국어로 요약
    """
    # Triple-quote f-string 올바르게 사용
    prompt = f"""다음 내용을 간결하게 한국어로 요약해줘 (최대 {max_chars}자):
{content}
"""
    return ask_openai(prompt)
