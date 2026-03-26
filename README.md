---
title: Email Triage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Email Triage OpenEnv

## Description
This environment simulates email triage where an AI agent:
- Classifies emails
- Assigns priority
- Generates replies

## Tasks
1. Classification (easy)
2. Prioritization (medium)
3. Reply Generation (hard)

## API Endpoints
- /reset
- /state
- /step
- /tasks

## Run Locally
pip install -r requirements.txt
uvicorn app.main:app --reload

## Baseline
python baseline.py