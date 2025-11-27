import asyncio
import httpx
from langchain_core.tools import tool

# Define all 6 service URLs
SERVICE_URLS = {
    "who_crew": "http://localhost:8001/run_who",
    "what_crew": "http://localhost:8002/run_what",
    "when_crew": "http://localhost:8003/run_when",
    "where_crew": "http://localhost:8004/run_where",
    "how_crew": "http://localhost:8005/run_how",
    "why_crew": "http://localhost:8006/run_why",
}

async def call_service(client, name, url, payload):
    """Helper function to make a single async POST request."""
    try:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return name, response.json()
    except httpx.RequestError as e:
        return name, {"error": f"Failed to call {name}: {str(e)}"}

@tool("Delegate to 5W1H Crews")
async def delegate_to_5w1h_crews(topic: str, plan: str) -> dict:
    """
    Delegates research to all 6 specialized (Who, What, When, Where, How, Why)
    CrewAI microservices IN PARALLEL.
    Returns a JSON object of all results.
    """
    print(f"--- 🛠️ Tool: Fanning out to 6 parallel microservices... ---")
    payload = {"topic": topic, "plan": plan}
    
    async with httpx.AsyncClient() as client:
        # Create a list of tasks to run concurrently
        tasks = []
        for name, url in SERVICE_URLS.items():
            tasks.append(call_service(client, name, url, payload))
            
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks)
        
    # Convert the list of (name, result) tuples into a dictionary
    compiled_results = {name: result for name, result in results}
    
    print(f"--- ✅ Tool: Received all 6 parallel responses. ---")
    return compiled_results
