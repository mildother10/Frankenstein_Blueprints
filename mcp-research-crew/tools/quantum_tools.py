import requests
from langchain_core.tools import tool

QUANTUM_SERVER_URL = "http://localhost:9000"

@tool("List Quantum Devices Tool")
def list_quantum_devices() -> str:
    """
    Fetches a list of all available quantum devices (computers and
    simulators) from the Quantum Server.
    """
    print("Tool: list_quantum_devices (calling Quantum Server at /devices)")
    try:
        response = requests.get(f"{QUANTUM_SERVER_URL}/devices")
        response.raise_for_status() 
        return response.json().get("devices", "Error: No devices key")
    except Exception as e:
        return f"Error connecting to Quantum Server: {e}"

@tool("Run Quantum Circuit Tool")
def run_quantum_circuit(qasm_circuit: str, device_id: str, shots: int = 1024) -> str:
    """
    Submits a quantum circuit (in QASM format) to the Quantum Server
    to be run on a specified 'device_id'.
    """
    print(f"Tool: run_quantum_circuit (calling Quantum Server at /run)")
    try:
        payload = {"qasm_circuit": qasm_circuit, "device_id": device_id, "shots": shots}
        response = requests.post(f"{QUANTUM_SERVER_URL}/run", json=payload)
        response.raise_for_status()
        return response.json().get("status", "Error: No status key")
    except Exception as e:
        return f"Error connecting to Quantum Server: {e}"

@tool("Check Quantum Job Status Tool")
def check_quantum_job_status(job_id: str) -> str:
    """
    Checks the status of a previously submitted quantum job by
    asking the Quantum Server.
    """
    print(f"Tool: check_quantum_job_status (calling Quantum Server at /status)")
    try:
        payload = {"job_id": job_id}
        response = requests.post(f"{QUANTUM_SERVER_URL}/status", json=payload)
        response.raise_for_status()
        return response.json().get("status", "Error: No status key")
    except Exception as e:
        return f"Error connecting to Quantum Server: {e}"
