import requests
from langchain_core.tools import tool

CODE_EXECUTOR_URL = "http://localhost:9090"

@tool("Execute Python Code Tool")
def execute_python_code(code: str, permission: bool = False) -> str:
    """
    Executes a block of safe, controlled Python code within an isolated sandbox.
    Requires 'permission=True' flag for human vetting/safety guardrails.
    Returns the execution status and output.
    """
    print(f"Tool: execute_python_code (Code Length: {len(code)}, Permission: {permission})")
    
    # Send the request to the new microservice
    try:
        payload = {"code": code, "permission": permission}
        response = requests.post(f"{CODE_EXECUTOR_URL}/execute", json=payload)
        response.raise_for_status()
        
        result = response.json()
        if result['status'] == "DENIED":
            # This simulates the HITL step: the agent must re-issue the command 
            # with the permission flag set after human review.
            return f"CODE EXECUTION DENIED. You must request execution with 'permission=True' after human review. Error: {result['error']}"
        
        return f"Code Execution Result (Status: {result['status']}):\n{result.get('output', result.get('error'))}"
        
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Executor Server: {e}. Check if Code Executor (Port 9090) is running."
