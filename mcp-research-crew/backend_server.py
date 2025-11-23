import uvicorn, json, os
from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from crew_runner import ResearchGraph
from tools.rag_tools import load_and_embed_notebooks
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

print("--- 🧠 [BackendServer] Loading ResearchGraph Engine... ---")
graph_runner = ResearchGraph()
print("--- ✅ [BackendServer] ResearchGraph Engine Loaded. ---")

@app.post("/run-research")
async def run_research(topic: str = Form(...)):
    
    async def run_research_stream(topic: str):
        print(f"\n--- �� [BackendServer] Kicking off graph for topic: {topic} ---")
        yield f'<div class="p-4 bg-gray-800 rounded-lg mb-4 border border-blue-600"><h3 class_="font-bold text-xl mb-2">🚀 Starting research for: {topic}</h3>'
        initial_state = {
            "research_topic": topic, "plan": "", "draft": "", "review": "",
            "final_report": "", "research_results": {}, "messages": [],
        }
        
        try:
            for step_output in graph_runner.graph.stream(initial_state, {"recursion_limit": 10}):
                last_node = list(step_output.keys())[-1]
                node_output = step_output[last_node]
                
                if last_node == "__end__":
                    pretty_output = f"Review:\n{node_output['review']}"
                elif isinstance(node_output, str):
                    pretty_output = node_output
                else:
                    pretty_output = json.dumps(node_output, indent=2)

                html_safe_output = pretty_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_chunk = f"""
                <div class="mb-4">
                    <h4 class="font-bold text-lg text-green-400">🧠 Node '{last_node}' executed:</h4>
                    <pre class="bg-gray-900 text-gray-300 p-3 mt-2 rounded-md overflow-x-auto text-sm whitespace-pre-wrap">{html_safe_output}</pre>
                </div>
                """
                yield html_chunk
            
            yield '<h3 class="font-bold text-xl mt-4 text-green-500">✅ Research Complete.</h3></div>'
            print("--- ✅ [BackendServer] Graph execution finished. ---")
            
        except Exception as e:
            yield f'<h3 class="font-bold text-xl mt-4 text-red-500">🔥 Graph Error:</h3><pre class="text-red-400">{e}</pre></div>'
            print(f"--- 🔥 [BackendServer] Graph execution error: {e} ---")

    return StreamingResponse(run_research_stream(topic), media_type="text/html")

if __name__ == "__main__":
    print("--- 🚀 [BackendServer] Initializing DLAI RAG Database... ---")
    load_and_embed_notebooks()
    print("--- 🚀 [BackendServer] Starting FastAPI 'Brain' Server on http://0.0.0.0:8000 ---")
    uvicorn.run(app, host="0.0.0.0", port=8000)
