from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import os

app = FastAPI()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

HTML = open("index.html").read()

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.post("/summarize")
async def summarize(request: Request):
    body = await request.json()
    note = body.get("note", "")
    prompt = f"""You are a clinical AI assistant. Summarize the following clinical note clearly and concisely for a physician. Extract: chief complaint, key findings, assessment, and plan.\n\nNote:\n{note}"""
    response = model.generate_content(prompt)
    return {"summary": response.text}