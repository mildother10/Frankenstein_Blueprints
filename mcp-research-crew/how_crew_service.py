import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.post("/run_how")
def run_crew(): return {"status": "DELEGATED", "result": "HowAgent Crew (port 8005) is researching code and implementation."}
if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8005)
