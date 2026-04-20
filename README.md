# VenueIQ — AI Event Intelligence System

AI-powered crowd management and event coordination system for large-scale sporting venues. Built for Google PromptWars Virtual | #BuildwithAI

## Problem
Crowd crushes, 25-min food queues, and staff coordination failures at major sporting events are preventable — but require real-time AI intelligence.

## Solution
VenueIQ uses Gemini 2.0 Flash to analyze live venue field reports across 3 modes:
- **Crowd Flow Analysis** — bottleneck detection, risk assessment, routing recommendations
- **Wait Time Optimization** — queue reduction plans with estimated improvements
- **Staff Coordination** — resource reallocation across Security, Ops, Medical, Transport

## Tech Stack
- Google Gemini 2.0 Flash
- FastAPI + Python 3.11
- Docker + Google Cloud Run (asia-south1)
- Vanilla JS frontend

## Live Demo
https://clinsumm-1010206561709.asia-south1.run.app

## Setup
```bash
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key
uvicorn main:app --reload
```

## Author
Faleha Qazi — B.Tech CSE (Health Informatics), VIT Bhopal University
