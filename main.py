# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from dotenv import load_dotenv

# ENV load
load_dotenv()

# Local imports
from src.kb.knowledge_loader import load_all_knowledge
from src.kb.knowledge_search import search_kb
from src.ai.ai_client import ask_openai
from src.ai.web_search import bing_search
from src.planner import generate_plan
from src.subscription import create_subscription, cancel_subscription, check_subscription

# FastAPI app
app = FastAPI(title="Sports AI Coach")

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load Knowledge Base at startup
KB = load_all_knowledge()


# -------------------------
# 1) INDEX PAGE
# -------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------
# 2) ASK API
# -------------------------
@app.post("/api/ask")
async def api_ask(payload: dict):
    question = payload.get("question", "")
    sport = payload.get("sport", "")

    if not question:
        return JSONResponse({"error": "question required"}, status_code=400)

    # 1) Local KB
    matches = search_kb(KB, question)

    if matches:
        top = matches[0]
        answer = (
            f"(local KB match: {top['key']}, score={top['score']})\n\n"
            f"{top['snippet']}"
        )
        return {"source": "local", "answer": answer, "matches": matches}

    # 2) Bing Web Fallback
    try:
        web = bing_search(question)
    except Exception:
        web = None

    if web:
        combined = "\n\n".join(
            [f"{w['name']}: {w['snippet']} ({w['url']})" for w in web]
        )
        prompt = (
            "You are an expert sports coach. "
            f"User asks: {question}. "
            "Synthesize the following web snippets into a concise answer in Korean:\n\n"
            f"{combined}"
        )
        synth = ask_openai(prompt)
        return {"source": "web", "answer": synth, "web": web}

    # 3) OpenAI fallback
    prompt = (
        "You are an expert coach for sports. "
        f"A user asks: {question}. "
        "Provide a concise, practical answer in Korean with 3 drills and precautions."
    )
    ai_resp = ask_openai(prompt)
    return {"source": "openai", "answer": ai_resp}


# -------------------------
# 3) PLAN API
# -------------------------
@app.post("/api/plan")
async def api_plan(payload: dict):
    user_id = payload.get("user_id", "anonymous")
    sport = payload.get("sport", "")
    goal = payload.get("goal", "")
    level = payload.get("level", "")

    premium = check_subscription(user_id)

    plan = generate_plan(sport, goal, level, premium=premium)

    if not premium:
        plan["premium_note"] = (
            "프리미엄(월 1,000원) 가입 시 추가 AI 보강 및 맞춤 분석이 제공됩니다."
        )

    return {"source": "planner", "plan": plan, "premium": premium}


# -------------------------
# 4) SUBSCRIBE API
# -------------------------
@app.post("/api/subscribe")
async def api_subscribe(payload: dict):
    user_id = payload.get("user_id")

    if not user_id:
        return JSONResponse({"error": "user_id required"}, status_code=400)

    info = create_subscription(user_id)
    return {"status": "created", "info": info}


# -------------------------
# 5) SUB STATUS API
# -------------------------
@app.get("/api/subscription_status")
async def api_subscription_status(user_id: str = None):
    if not user_id:
        return JSONResponse({"error": "user_id required"}, status_code=400)

    ok = check_subscription(user_id)
    return {"user_id": user_id, "active": ok}
