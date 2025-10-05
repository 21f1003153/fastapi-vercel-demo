from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Load data --------
data_path = Path(__file__).parent.parent / "q-vercel-latency.json"
df = pd.read_json(data_path)

@app.get("/")
def read_root():
    return {"message": "Hello, this is the latency API!"}

@app.post("/metrics")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        region_data = df[df["region"] == region]

        if region_data.empty:
            continue

        avg_latency = region_data["latency_ms"].mean()
        p95_latency = np.percentile(region_data["latency_ms"], 95)
        avg_uptime = region_data["uptime"].mean()
        breaches = (region_data["latency_ms"] > threshold).sum()

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": int(breaches),
        }

    return result
