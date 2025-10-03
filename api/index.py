from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
from pathlib import Path

app = FastAPI()

# Enable CORS (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON dataset at startup
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "q-vercel-latency.json"
with open(DATA_PATH, "r") as f:
    telemetry = pd.DataFrame(json.load(f))

@app.post("/metrics")
async def get_metrics(req: Request):
    body = await req.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 200)

    result = {}
    for region in regions:
        df = telemetry[telemetry["region"] == region]
        if df.empty:
            continue

        latencies = df["latency_ms"].to_numpy()
        uptimes = df["uptime_pct"].to_numpy()

        result[region] = {
            "avg_latency": round(latencies.mean(), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(uptimes.mean() / 100, 3),  # convert pct to fraction
            "breaches": int((latencies > threshold).sum())
        }

    return result
