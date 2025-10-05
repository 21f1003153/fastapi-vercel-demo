# api/index.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path

# -------- Setup FastAPI --------
app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains (safe for assignments)
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


# -------- Request Schema --------
class MetricsRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

# -------- Load data --------
data_path = Path(__file__).parent.parent / "data" / "q-vercel-latency.json"
df = pd.read_json(data_path)

# Load telemetry data (your JSON file)
with open(Path(__file__).parent / "../q-vercel-latency.json") as f:
    telemetry_data = json.load(f)

df = pd.DataFrame(telemetry_data)

# -------- Routes --------
@app.get("/")
def read_root():
    return {"message": "Hello, this is the latency API!"}

# @app.post("/metrics")
# def metrics(request: MetricsRequest) -> Dict[str, Any]:
#     regions = request.regions
#     threshold = request.threshold_ms

#     result = {}

#     for region in regions:
#         region_data = df[df["region"] == region]

#         if region_data.empty:
#             continue  # skip if no data for that region

#         #avg_latency = region_data["latency_ms"].mean()
#         avg_latency = region_data["latency_ms"].mean()

#         p95_latency = region_data["latency_ms"].quantile(0.95)
#         #avg_uptime = region_data["uptime"].mean()
#         avg_uptime = region_data["uptime_pct"].mean()

#         breaches = (region_data["latency_ms"] > threshold).sum()

#         result[region] = {
#             "avg_latency": round(avg_latency, 2),
#             "p95_latency": round(p95_latency, 2),
#             "avg_uptime": round(avg_uptime, 2),
#             "breaches": int(breaches)
#         }

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
