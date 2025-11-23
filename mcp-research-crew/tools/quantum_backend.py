import os
from qbraid import QbraidProvider, QbraidJob
from dotenv import load_dotenv

load_dotenv() 

try:
    print("Initializing QbraidProvider...")
    provider = QbraidProvider()
    print("✅ QbraidProvider initialized.")
except Exception as e:
    print(f"Warning: Could not initialize QbraidProvider. {e}")
    provider = None

def list_quantum_devices() -> str:
    print("QuantumBackend: list_quantum_devices")
    if provider is None: return "Error: QbraidProvider failed to initialize."
    try:
        devices = provider.get_devices()
        if not devices: return "No quantum devices found."
        device_list = [f"- ID: {d.id}\n  Name: {d.name}\n  Status: {'online' if d.is_online() else 'offline'}\n  Qubits: {d.n_qubits}\n" for d in devices]
        return "\n".join(device_list)
    except Exception as e:
        return f"Error fetching Qbraid devices: {e}"

def run_quantum_circuit(qasm_circuit: str, device_id: str, shots: int = 1024) -> str:
    print(f"QuantumBackend: run_quantum_circuit (Device: {device_id})")
    if provider is None: return "Error: QbraidProvider failed to initialize."
    try:
        device = provider.get_device(device_id)
        if not device: return f"Error: Device ID '{device_id}' not found."
        jobs = device.run([qasm_circuit], shots=shots)
        job = jobs[0]
        return f"Job ID: {job.id}, Status: {job.status()}"
    except Exception as e:
        return f"Error submitting quantum job: {e}"

def check_quantum_job_status(job_id: str) -> str:
    print(f"QuantumBackend: check_quantum_job_status (Job ID: {job_id})")
    try:
        job = QbraidJob(job_id)
        status = job.status()
        if status == "COMPLETED":
            results = job.result()
            return f"Job Status: COMPLETED, Results: {results.data.get_counts()}"
        elif status == "FAILED":
            return f"Job Status: FAILED, Error: {job.error_message()}"
        else:
            return f"Job Status: {status}"
    except Exception as e:
        return f"Error checking quantum job status: {e}"
