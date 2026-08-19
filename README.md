# AI-Driven Cyclone & Coastal Disaster Early Warning System

Multi-agent IBM Watsonx.ai system with 5 specialist AI agents for cyclone and coastal disaster management.

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open **http://localhost:8000** in your browser.

## API Docs

Interactive Swagger UI: **http://localhost:8000/docs**

## Architecture

```
orchestrator.py  ←─ coordinates all agents in parallel
│
├── agents/cyclone_prediction.py    Agent 1: Track & Intensity Prediction
├── agents/fishermen_alert.py       Agent 2: Fishermen Safety Alert
├── agents/evacuation_planning.py   Agent 3: Evacuation Route Planning
├── agents/resource_coordination.py Agent 4: Relief Resource Coordination
└── agents/damage_assessment.py     Agent 5: Post-Disaster Damage Assessment

watsonx_client.py  ←─ IBM IAM token + Watsonx.ai generation API
config.py          ←─ credentials & endpoints
main.py            ←─ FastAPI REST backend
static/index.html  ←─ full-stack web dashboard
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/agents/cyclone-prediction` | Agent 1 — storm track & intensity |
| POST | `/agents/fishermen-alert` | Agent 2 — coastal boat alerts |
| POST | `/agents/evacuation-plan` | Agent 3 — phased evacuation planning |
| POST | `/agents/resource-coordination` | Agent 4 — relief logistics |
| POST | `/agents/damage-assessment` | Agent 5 — post-disaster assessment |
| POST | `/orchestrate/pre-landfall` | All 4 pre-landfall agents in parallel |
| POST | `/orchestrate/post-landfall` | Damage + Resources agents in parallel |
| GET  | `/health` | Health check |
| GET  | `/` | Web dashboard |

## IBM Watsonx.ai Configuration

- **Model**: `ibm/granite-4-h-small`
- **Region**: `eu-de` (Frankfurt)
- **Project ID**: `6e881b4d-c78d-4581-9880-7c89408fe65f`
- **API Version**: `2023-05-29`
