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

@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    report = body.get("report", "")
    mode = body.get("mode", "crowd")

    prompts = {
        "crowd": f"""You are an AI crowd intelligence system for large-scale sporting venues. Analyze the following crowd report and provide:
1. CROWD STATUS: Current situation assessment (1-2 sentences)
2. RISK LEVEL: Low / Medium / High / Critical with reason
3. BOTTLENECKS: Specific problem areas identified
4. IMMEDIATE ACTIONS: 3-5 concrete steps for staff right now
5. ROUTING RECOMMENDATION: Suggested crowd flow changes

Report:
{report}""",
        "wait": f"""You are an AI queue optimization system for large-scale sporting venues. Analyze the following waiting time report and provide:
1. WAIT ANALYSIS: Summary of current queue situation
2. WORST AREAS: Top 3 highest wait time locations
3. ROOT CAUSE: Why these queues are forming
4. OPTIMIZATION PLAN: 3-5 specific actions to reduce wait times
5. ESTIMATED IMPROVEMENT: Expected wait time reduction if actions taken

Report:
{report}""",
        "coord": f"""You are an AI event coordination system for large-scale sporting venues. Analyze the following coordination report and provide:
1. SITUATION OVERVIEW: What is happening across the venue
2. COMMUNICATION GAPS: Where coordination is breaking down
3. RESOURCE ALLOCATION: Staff/resources that need redeployment
4. ACTION ITEMS: Specific tasks for each team (Security, Operations, Medical, Transport)
5. PRIORITY ORDER: What to address first and why

Report:
{report}"""
    }

    prompt = prompts.get(mode, prompts["crowd"])
    response = model.generate_content(prompt)
    return {"analysis": response.text}
