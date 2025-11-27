import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.post("/run_when")
def run_crew(): return {"status": "DELEGATED", "result": "WhenAgent Crew (port 8003) is researching timelines and history."}
if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8003)
