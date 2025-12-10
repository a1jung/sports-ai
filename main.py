from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

class AskRequest(BaseModel):
    category: str
    subcategory: str
    question: str

def ask_gpt(knowledge, question):
    prompt = f"{knowledge}\n질문: {question}"
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role':'user','content':prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

@app.post("/ask")
def ask_question(req: AskRequest):
    file_path = f"data/{req.category}/{req.subcategory}/description.json"
    with open(file_path, "r", encoding="utf-8") as f:
        knowledge = f.read()
    answer = ask_gpt(knowledge, req.question)
    return {"answer": answer}
