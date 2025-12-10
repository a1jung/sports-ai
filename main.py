from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# CORS 설정 (모든 출처 허용, Render용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

knowledge_base = {
    "요트": "요트는 바람의 힘을 이용해 이동하며 세일 트림과 밸런스가 핵심입니다.",
    "체조": "기계체조는 신체조절능력, 코어 안정성, 유연성이 매우 중요합니다.",
    "야구": "야구 투수는 회전근개 안정성과 하체 힘 전달이 핵심입니다.",
    "아이스하키": "아이스하키는 공격·수비·골리 포지션이 있으며 빠른 스케이팅이 핵심입니다."
}

def make_recommendations(text):
    if "요트" in text:
        return ["요트 세일 트림 방법", "레이저 요트 팁", "요트 바람 읽는 법"]
    if "체조" in text:
        return ["유연성 루틴", "평행봉 팁", "체조 기본 훈련"]
    if "야구" in text:
        return ["하체 강화 루틴", "투수 어깨 안 아프게 던지는 법", "구속 올리는 법"]
    if "아이스하키" in text:
        return ["하키 스케이팅 팁", "공격 패턴", "수비 움직임"]
    return ["요트는 어떻게 타?", "체조 루틴 추천", "야구 훈련 설명", "아이스하키 포지션 설명"]

def generate_answer(text):
    for key in knowledge_base:
        if key in text:
            return knowledge_base[key]
    return "아직 해당 질문에 대한 전문 지식이 부족합니다."

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_text = data.get("message", "")
    ai_answer = generate_answer(user_text)
    recommendations = make_recommendations(user_text)

    return JSONResponse({
        "answer": ai_answer,
        "recommendations": recommendations
    })

@app.get("/")
def root():
    return FileResponse("static/index.html")

