# 🏅 Sports AI Project

AI 기반 스포츠 훈련 가이드 제공 시스템  
FastAPI + JSON 데이터 + 간단한 웹 UI 기반 프로젝트입니다.

---

## 🚀 기능 요약

### ✔ FastAPI REST API
- 실제 JSON 파일을 자동으로 읽어 스포츠 정보를 제공
- 종목/포지션별 데이터 탐색 가능

### ✔ 웹 UI 페이지 제공
- /에서 index.html 렌더링
- /static/ 경로로 CSS, JS 연결

### ✔ GitHub Push 자동화 스크립트 포함
- push.ps1 한 번 실행으로 자동 commit + push

---

## 📁 Project Structure

\\\
sports-ai/
├─ data/
│  ├─ baseball/
│  ├─ gymnastics/
│  ├─ IceHockey/
│  ├─ yacht/
│  └─ fitness_knowledge.json
│
├─ static/
│  ├─ style.css
│  └─ script.js
│
├─ templates/
│  └─ index.html
│
├─ main.py
├─ push.ps1
├─ requirements.txt
└─ start.sh
\\\

---

## 🔥 API 사용 예

| Endpoint | 설명 |
|---------|------|
| /api/baseball/catcher | 야구 포수 |
| /api/IceHockey/forwards | 아이스하키 포워드 |
| /api/gymnastics/gymnastics_men | 체조 남자 |
| / | 웹페이지 렌더링 |

---

## ▶ 실행 방법

### 1) 패키지 설치

\\\bash
pip install -r requirements.txt
\\

### 2) 서버 실행

\\\bash
uvicorn main:app --reload
\\

### 3) 접속주소  
http://localhost:8000

---

## 👤 Author  
**a1jung**
