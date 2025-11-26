# main.py
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
from src.ai.ai_client import ask_openai, summarize_text
from src.ai.web_search import bing_search

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
    # expected: { "sport": "baseball", "question": "포수 훈련법 알려줘", "user_id": "optional" }
    sport = payload.get('sport') or ''
    question = payload.get('question') or ''
    if not question:
        return JSONResponse({'error': 'question required'}, status_code=400)

    # 1) try local KB search
    matches = search_kb(KB, question)
    if matches:
        # take top match
        top = matches[0]
        answer = f\"(local KB match: {top['key']}, score={top['score']})\\n\\n{top['snippet']}\"
        return {'source': 'local', 'answer': answer, 'matches': matches}

    # 2) try web search (Bing) if available
    web = None
    try:
        web = bing_search(question)
    except Exception:
        web = None
    if web:
        # summarize web snippets via OpenAI
        combined = '\\n\\n'.join([f\"{w['name']}: {w['snippet']} ({w['url']})\" for w in web])
        # ask OpenAI to synthesize
        prompt = f\"You are an expert sports coach. A user asks: {question}. Synthesize the following web snippets into a concise answer in Korean:\\n\\n{combined}\"
        synth = ask_openai(prompt)
        return {'source': 'web', 'answer': synth, 'web': web}

    # 3) fallback to OpenAI directly
    prompt = f\"You are an expert coach for sports. A user asks: {question}. Provide a concise, practical answer in Korean with 3 drills and precautions.\"
    ai_resp = ask_openai(prompt)
    return {'source': 'openai', 'answer': ai_resp}
