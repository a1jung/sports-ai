# main.py (updated)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, json
from dotenv import load_dotenv

# load env
load_dotenv()

from src.kb.knowledge_loader import load_all_knowledge
from src.kb.knowledge_search import search_kb
from src.ai.ai_client import ask_openai
from src.ai.web_search import bing_search
from src.planner import generate_plan
from src.subscription import create_subscription, cancel_subscription, check_subscription

app = FastAPI(title='Sports AI Coach')

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

# Load KB at startup
KB = load_all_knowledge()

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/api/ask')
async def api_ask(payload: dict):
    question = payload.get('question') or ''
    sport = payload.get('sport') or ''
    if not question:
        return JSONResponse({'error':'question required'}, status_code=400)
    matches = search_kb(KB, question)
    if matches:
        top = matches[0]
        answer = f\"(local KB match: {top['key']}, score={top['score']})\\n\\n{top['snippet']}\"
        return {'source':'local','answer':answer,'matches':matches}
    # web fallback
    web = None
    try:
        web = bing_search(question)
    except Exception:
        web = None
    if web:
        combined = '\\n\\n'.join([f\"{w['name']}: {w['snippet']} ({w['url']})\" for w in web])
        prompt = f\"You are an expert sports coach. User asks: {question}. Synthesize the following web snippets into a concise answer in Korean:\\n\\n{combined}\"
        synth = ask_openai(prompt)
        return {'source':'web','answer':synth,'web':web}
    # openai fallback
    prompt = f\"You are an expert coach for sports. A user asks: {question}. Provide a concise, practical answer in Korean with 3 drills and precautions.\"
    ai_resp = ask_openai(prompt)
    return {'source':'openai','answer':ai_resp}

@app.post('/api/plan')
async def api_plan(payload: dict):
    # expected payload: { "user_id": "...", "sport":"baseball", "goal":"...", "level":"beginner" }
    user_id = payload.get('user_id') or 'anonymous'
    sport = payload.get('sport') or ''
    goal = payload.get('goal') or ''
    level = payload.get('level') or ''
    premium = check_subscription(user_id)
    plan = generate_plan(sport, goal, level, premium=premium)
    # If not premium, include info about premium features
    if not premium:
        plan['premium_note'] = '프리미엄(월 1,000원) 가입 시 추가 AI 보강 및 맞춤 분석 제공됩니다.'
    return {'source':'planner','plan':plan, 'premium':premium}

@app.post('/api/subscribe')
async def api_subscribe(payload: dict):
    # Mock subscription activation. In real scenario, integrate with Stripe/PG and confirm via webhook.
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

