import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.post("/run_what")
def run_crew(): return {"status": "DELEGATED", "result": "WhatAgent Crew (port 8002) is researching concepts and definitions."}
if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8002)
