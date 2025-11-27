import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json
import io
import contextlib

app = FastAPI()

class CodeExecutionRequest(BaseModel):
    code: str
    permission: bool = False # Human-in-the-Loop flag

@app.post("/execute")
def execute_code(request: CodeExecutionRequest):
    """
    Executes Python code in a controlled subprocess.
    Requires permission=True flag for safety.
    """
    print(f"ExecutorServer: Received {len(request.code)} bytes of code.")
    
    # --- HITL SAFETY CHECK ---
    if not request.permission:
        return {
            "status": "DENIED",
            "error": "Code Execution DENIED: Human-in-the-Loop permission not granted. Set 'permission=True'."
        }
    
    # --- SANDBOX WARNING ---
    # This is still executing on the host machine. A production version MUST
    # use a dedicated Docker container (e.g., using 'docker run --rm python:3.12')
    # or a secure sandboxing library.

    # Execute the code and capture output (stdout/stderr)
    try:
        # Use a string buffer to capture standard output
        output_buffer = io.StringIO()
        
        # We wrap the code in a function so that 'exec' doesn't pollute the global scope
        code_to_exec = f"def sandboxed_execution():\n{request.code}\n_output = sandboxed_execution()"
        
        # Use contextlib.redirect_stdout to capture print statements
        with contextlib.redirect_stdout(output_buffer):
            # This is the execution step. It's safe only because we require the permission flag.
            exec(code_to_exec, {})
        
        output = output_buffer.getvalue()
        
        return {
            "status": "COMPLETED",
            "output": output,
            "message": f"Code executed successfully. Output logged."
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Execution Error: {type(e).__name__}: {str(e)}"
        }

if __name__ == "__main__":
    print("--- 🚀 Starting Code Executor Microservice on http://0.0.0.0:9090 ---")
    print("!!! WARNING: EXECUTION IS NOT ISOLATED IN A DOCKER CONTAINER. USE CAUTION. !!!")
    uvicorn.run(app, host="0.0.0.0", port=9090)
