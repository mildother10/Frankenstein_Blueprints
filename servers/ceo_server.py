# "Hulk Smash 36.0" (Master Blueprint)
# This is the "CEO" (v5.0 "Manager") server
# It runs on the "Dumb" (v28.0) (CPU) (v35.0) base
from fastapi import FastAPI, BackgroundTasks
import aiohttp
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# "C-Suite" (v17.0) Agent URLs (from docker-compose)
CTO_URL = "http://cto_server:8007"
CHRO_URL = "http://chro_server:8008"
CIO_URL = "http://cio_server:8009"
LIBRARIAN_URL = "http://librarian_server:8003"
# ...etc.

async def run_mission(mission: dict):
    """
    This is the "Hulk" (v28.0) (asyncio v26.0) "Macro-Swarm" logic.
    It runs the "Parallel" (v26.0) R&D loop.
    """
    logging.info(f"CEO (v5.0) executing mission: {mission['mission_id']}")
    
    # 1. "Hulk Smash" (v28.0) (hire) the "Scientist" (v35.0) (CTO)
    try:
        async with aiohttp.ClientSession() as session:
            # Tell CTO to start R&D
            async with session.post(f"{CTO_URL}/execute_rd", json=mission) as cto_response:
                cto_result = await cto_response.json()
                logging.info(f"CTO (v30.0) finished work: {cto_result}")
                
            # 2. "Hulk Smash" (v28.0) (hire) the "R&D Loop" (v23.0) (CHRO)
            # Send the CTO's "dumb" (v28.0) work to the "Critique Agent" (v23.0)
            async with session.post(f"{CHRO_URL}/critique", json=cto_result) as chro_response:
                critique = await chro_response.json()
                logging.info(f"CHRO (v23.0) critique complete: {critique}")

            # 3. "Smash" (v28.0) (save) the "Professor" (v33.0) result to "Corporate Memory" (v21.0)
            async with session.post(f"{LIBRARIAN_URL}/save", json=critique) as lib_response:
                logging.info("Mission result saved to Librarian (v21.0).")

    except Exception as e:
        logging.error(f"CEO (v5.0) Mission Failed: {e}")

@app.post("/delegate_task")
async def delegate_task(mission: dict, background_tasks: BackgroundTasks):
    """
    This is the "Hulk Smash 32.0" endpoint.
    It *only* accepts "clean" (v29.0) (structured JSON) from the "EA_server" (v32.0).
    """
    logging.info(f"CEO (v5.0) received structured mission: {mission['mission_id']}")
    
    # "Hulk Smash" (v28.0) (run) the "v23.0" (Mandatory R&D) loop in the background
    background_tasks.add_task(run_mission, mission)
    
    return {"status": "acknowledged", "mission_id": mission['mission_id']}

@app.get("/")
def read_root():
    return {"message": "CEO_server (v5.0 'Manager') is operational."}
