import json
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pegase Parser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "last_data.json")


@app.get("/")
def root():
    return {"status": "ok", "message": "Pegase Parser API"}


@app.get("/data")
def get_data():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Aucune donnée disponible")
    
    last_modified = os.path.getmtime(DATA_FILE)
    last_refresh = datetime.fromtimestamp(last_modified).isoformat()
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {
        "last_refresh": last_refresh,
        "data": data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
