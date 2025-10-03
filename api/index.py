from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
from pathlib import Path

app = FastAPI()

# Enable CORS for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data (your JSON file)
with open(Path(__file__).parent / "../q-vercel-latency.json") as f:
    telemetry_data = json.load(f)

df = pd.DataFrame(telemetry_data)

@app.get("/")
def read_root():
    return {"message": "Hello, World"}

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
