# main.py (Jinja2 제거, JSON 중심)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

from src.kb.knowledge_loader import load_all_knowledge
from src.kb.knowledge_search import search_kb
from src.ai.ai_client import ask_openai
from src.ai.web_search import bing_search
from src.planner import generate_plan
from src.subscription import create_subscription, cancel_subscription, check_subscription

app = FastAPI(title='Sports AI Coach')

# Load KB at startup
KB = load_all_knowledge()

@app.get('/')
def index():
    return {'message': 'Sports AI Coach API is running', 'routes': ['/api/ask', '/api/plan', '/api/subscribe', '/api/subscription_status']}

@app.post('/api/ask')
async def api_ask(payload: dict):
    question = payload.get('question') or ''
    sport = payload.get('sport') or ''
    if not question:
        return JSONResponse({'error':'question required'}, status_code=400)
    
    # Local KB 검색
    matches = search_kb(KB, question)
    if matches:
        top = matches[0]
        answer = f"(local KB match: {top['key']}, score={top['score']})\n\n{top['snippet']}"
        return {'source':'local','answer':answer,'matches':matches}

    # Web 검색 fallback
    web = None
    try:
        web = bing_search(question)
    except Exception:
        web = None
    if web:
        combined = '\n\n'.join([f"{w['name']}: {w['snippet']} ({w['url']})" for w in web])
        prompt = f"You are an expert sports coach. User asks: {question}. Synthesize the following web snippets into a concise answer in Korean:\n\n{combined}"
        synth = ask_openai(prompt)
        return {'source':'web','answer':synth,'web':web}

    # OpenAI fallback
    prompt = f"You are an expert coach for sports. A user asks: {question}. Provide a concise, practical answer in Korean with 3 drills and precautions."
    ai_resp = ask_openai(prompt)
    return {'source':'openai','answer':ai_resp}

@app.post('/api/plan')
async def api_plan(payload: dict):
    user_id = payload.get('user_id') or 'anonymous'
    sport = payload.get('sport') or ''
    goal = payload.get('goal') or ''
    level = payload.get('level') or ''
    premium = check_subscription(user_id)
    plan = generate_plan(sport, goal, level, premium=premium)
    if not premium:
        plan['premium_note'] = '프리미엄(월 1,000원) 가입 시 추가 AI 보강 및 맞춤 분석 제공됩니다.'
    return {'source':'planner','plan':plan, 'premium':premium}

@app.post('/api/subscribe')
async def api_subscribe(payload: dict):
    user_id = payload.get('user_id') or None
    if not user_id:
        return JSONResponse({'error':'user_id required'}, status_code=400)
    info = create_subscription(user_id)
    return {'status':'created','info':info}

@app.get('/api/subscription_status')
async def api_subscription_status(user_id: str = None):
    if not user_id:
        return JSONResponse({'error':'user_id required'}, status_code=400)
    ok = check_subscription(user_id)
    return {'user_id':user_id,'active':ok}
