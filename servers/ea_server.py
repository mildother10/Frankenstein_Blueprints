# "Hulk Smash 36.0" (Master Blueprint)
# This is the "EA_server" (v32.0 "Padded Layer")
# It runs on the "Dumb" (v28.0) (CPU) (v35.0) base
from fastapi import FastAPI
import aiohttp
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

CEO_URL = "http://ceo_server:8001" # Service name from docker-compose

@app.post("/mission")
async def create_mission(prompt: str):
    """
    This is the "Hulk Smash 32.0" (Padded Layer) endpoint.
    1. It "smashes" (v28.0) (sanitizes) the prompt ("Doorkeeper").
    2. It "smashes" (v28.0) (translates) the prompt ("Translator").
    3. It "smashes" (v28.0) (delegates) the structured JSON to the CEO.
    """
    logging.info(f"EA_server (v32.0) received raw prompt: {prompt}")

    # Job 1: "Doorkeeper" (v32.0) - Sanitize for prompt injection
    if "nefarious_keyword" in prompt.lower():
        logging.warning("Nefarious prompt injection detected. Mission aborted.")
        return {"status": "denied", "reason": "Prompt injection detected."}

    # Job 2: "Translator" (v32.0) - Structure the prompt
    # (This will eventually be an LLM call on the "cheap/gpu" base)
    structured_prompt_json = {
        "mission_id": "mission_123",
        "raw_prompt": prompt,
        "task": "Perform R&D scan",
        "parameters": {"source": "arXiv", "keywords": ["quantum", prompt]}
    }
    
    logging.info(f"EA_server (v32.0) delegating structured mission to CEO_server...")

    # Job 3: "Delegate" - Send to CEO (v5.0 "Manager")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{CEO_URL}/delegate_task", json=structured_prompt_json) as response:
                response_data = await response.json()
                return {"status": "delegated", "ceo_response": response_data}
    except Exception as e:
        logging.error(f"Failed to delegate to CEO: {e}")
        return {"status": "error", "message": "Failed to contact CEO_server."}

@app.get("/")
def read_root():
    return {"message": "EA_server (v32.0 'Padded Layer') is operational."}
