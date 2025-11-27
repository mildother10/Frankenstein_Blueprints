import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from tools.quantum_backend import (
    list_quantum_devices, 
    run_quantum_circuit, 
    check_quantum_job_status
)

app = FastAPI()

class CircuitJobRequest(BaseModel):
    qasm_circuit: str
    device_id: str
    shots: int = 1024

class JobStatusRequest(BaseModel):
    job_id: str

@app.get("/devices")
def get_devices():
    print("QuantumServer: Received request for /devices")
    return {"devices": list_quantum_devices()}

@app.post("/run")
def submit_job(request: CircuitJobRequest):
    print(f"QuantumServer: Received request for /run on device {request.device_id}")
    result = run_quantum_circuit(
        qasm_circuit=request.qasm_circuit,
        device_id=request.device_id,
        shots=request.shots
    )
    return {"status": result}

@app.post("/status")
def get_job_status(request: JobStatusRequest):
    print(f"QuantumServer: Received request for /status on job {request.job_id}")
    result = check_quantum_job_status(job_id=request.job_id)
    return {"status": result}

if __name__ == "__main__":
    print("--- 🚀 Starting Quantum Microservice on http://0.0.0.0:9000 ---")
    uvicorn.run(app, host="0.0.0.0", port=9000)
