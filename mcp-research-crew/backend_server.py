import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crew_runner import ResearchGraph
from tools.rag_tools import load_and_embed_notebooks

# --- THE FIX: Run the RAG tool setup ONCE on startup ---
print("--- [BackendServer] Starting... ---")
print("--- [BackendServer] Initializing DLAI Knowledge Base... ---")
try:
    load_and_embed_notebooks()
    print("--- [BackendServer] DLAI Knowledge Base is READY. ---")
except Exception as e:
    print(f"--- [BackendServer] CRITICAL: Failed to initialize RAG tools: {e} ---")
# ---

# Initialize the ResearchGraph
try:
    research_graph = ResearchGraph()
    print("--- [BackendServer] ResearchGraph is READY. ---")
except Exception as e:
    print(f"--- [BackendServer] CRITICAL: Failed to initialize ResearchGraph: {e} ---")

app = FastAPI()

# CORS Middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str
    plan: str

# --- THE FINAL ASYNC FIX ---
@app.post("/run-research")
async def run_research(request: ResearchRequest):
    """
    Asynchronously runs the research graph.
    """
    print(f"--- [BackendServer] Received research request for: {request.topic} ---")
    try:
        topic = request.topic
        plan = request.plan
        
        initial_state = {"research_topic": topic, "plan": plan}
        
        # Use .ainvoke() for the async graph
        print("--- [BackendServer] A-Invoking ResearchGraph... ---")
        result = await research_graph.graph.ainvoke(initial_state)
        print("--- [BackendServer] ResearchGraph A-Invoke Complete. ---")
        
        final_draft = result.get('draft', 'No draft found.')
        return {"result": final_draft}
        
    except Exception as e:
        print(f"--- [BackendServer] ERROR during research: {e} ---")
        return {"result": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    print("--- [BackendServer] Starting Uvicorn on http://0.0.0.0:8000 ---")
    uvicorn.run(app, host="0.0.0.0", port=8000)
