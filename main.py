from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
import os

app = FastAPI()

# static 및 templates 연결
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# -------------------------
# 1) 루트 웹페이지 렌더링
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------
# 2) JSON 자동 로딩 함수
# -------------------------
def load_json(category: str, name: str):
    base_path = os.path.join("data", category)

    # 기본 JSON (예: data/baseball/catcher.json)
    file_path = os.path.join(base_path, f"{name}.json")

    # 폴더 구조가 있는 스포츠(IceHockey, yacht 등)
    if not os.path.exists(file_path):
        nested_dir = os.path.join(base_path, name)
        if os.path.isdir(nested_dir):
            file_path = os.path.join(nested_dir, "description.json")

    if not os.path.exists(file_path):
        return {"error": "file not found"}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# 3) API 엔드포인트
# -------------------------
@app.get("/api/{category}/{name}")
def get_sports_data(category: str, name: str):
    return load_json(category, name)
