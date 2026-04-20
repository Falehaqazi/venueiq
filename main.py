from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VenueIQ", description="AI Event Intelligence System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

VALID_MODES = {"crowd", "wait", "coord"}
MAX_REPORT_LENGTH = 5000
MIN_REPORT_LENGTH = 10

with open("index.html") as f:
    HTML = f.read()

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/health")
def health():
    return {"status": "healthy", "service": "VenueIQ", "version": "2.0.0"}

@app.post("/analyze")
async def analyze(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    report = body.get("report", "").strip()
    mode = body.get("mode", "crowd").strip().lower()

    if not report:
        raise HTTPException(status_code=400, detail="Report field is required")
    if len(report) < MIN_REPORT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Report too short (min {MIN_REPORT_LENGTH} chars)")
    if len(report) > MAX_REPORT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Report too long (max {MAX_REPORT_LENGTH} chars)")
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {VALID_MODES}")

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

    try:
        response = model.generate_content(prompts[mode])
        logger.info(f"Analysis completed: mode={mode}, report_length={len(report)}")
        return {"analysis": response.text, "mode": mode, "status": "success"}
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=500, detail="AI analysis failed. Please try again.")
