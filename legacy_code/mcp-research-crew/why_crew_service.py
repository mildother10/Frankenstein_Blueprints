import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.post("/run_why")
def run_crew(): return {"status": "DELEGATED", "result": "WhyAgent Crew (port 8006) is researching impact and motivation."}
if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8006)
