import uvicorn
from fastapi import FastAPI
app = FastAPI()
@app.post("/run_where")
def run_crew(): return {"status": "DELEGATED", "result": "WhereAgent Crew (port 8004) is researching sources and libraries."}
if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8004)
