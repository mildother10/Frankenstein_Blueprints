import uvicorn, os
from pyngrok import ngrok
from fasthtml.core import FastHTML
from fasthtml.common import *
from dotenv import load_dotenv

load_dotenv()

BACKEND_SERVER_URL = "http://localhost:8000"
app = FastHTML()
rt = app.route

@rt("/")
def main_page():
    return Title("MCP Research Crew"),            Head(
               Script(src="https://cdn.tailwindcss.com"),
               Script(src="https://unpkg.com/htmx.org@1.9.12"),
               # --- JAVASCRIPT FOR TIMER ---
               Script('''
                   let startTime;
                   let timerInterval;

                   function startTimer() {
                       startTime = Date.now();
                       const timerDisplay = document.getElementById('timer-display');
                       timerDisplay.innerText = '00:00';
                       timerDisplay.classList.remove('hidden');

                       timerInterval = setInterval(() => {
                           const elapsed = Date.now() - startTime;
                           const seconds = Math.floor(elapsed / 1000) % 60;
                           const minutes = Math.floor(elapsed / 1000 / 60);
                           timerDisplay.innerText = 
                               String(minutes).padStart(2, '0') + ':' + 
                               String(seconds).padStart(2, '0');
                       }, 1000);
                   }

                   function stopTimer() {
                       clearInterval(timerInterval);
                       const timerDisplay = document.getElementById('timer-display');
                       timerDisplay.classList.add('hidden');
                   }
               ''')
           ),            Body(
               Div(
                   H1("📚 Quantum-Validated MCP Research Crew (Microservice Arch)", cls="text-3xl font-bold mb-4"),
                   P("Enter your research topic below to kick off the autonomous A2A LangGraph crew.", cls="mb-6 text-gray-400"),
                   # --- TIMER DISPLAY ---
                   Div(
                       P("Processing Time: ", cls="text-sm text-gray-400 inline-block"),
                       P(id="timer-display", cls="text-xl font-mono text-yellow-400 ml-2 hidden inline-block")
                   ),
                   
                   Form(
                       # --- CHANGED INPUT TO TEXTAREA FOR WRAPPING ---
                       Textarea(name="topic", placeholder="e.g., 'I need a step-by-step plan for a paper on quantum machine learning...' Use the enter key for wrapping.", rows="4",
                             cls="flex-grow bg-gray-700 border border-gray-600 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"),
                       Button("🚀 Run Research", type="submit",
                              cls="bg-blue-600 hover:bg-blue-700 rounded-lg px-4 py-2 font-semibold"),
                       cls="flex space-x-2",
                       hx_post=f"{BACKEND_SERVER_URL}/run-research",
                       hx_target="#results-container",
                       hx_swap="beforeend",
                       hx_indicator="#loading-spinner",
                       # --- HTMX HOOKS FOR TIMER ---
                       hx_on_submit="startTimer()",
                       hx_on_after_swap="stopTimer()" # Stops timer when results are streamed back
                   ),
                   Div(id="results-container", cls="mt-8"),
                   Div("🌀 Thinking...", id="loading-spinner", cls="htmx-indicator mt-4 text-lg text-blue-400", style="display:none;"),
                   Style(".htmx-indicator{display:none;} .htmx-request .htmx-indicator{display:inline;}")
               ),
               cls="bg-gray-900 text-white p-8"
           )

if __name__ == "__main__":
    print("--- 🚀 [FrontendServer] Creating public tunnel with ngrok... ---")
    authtoken = os.environ.get("NGROK_AUTHTOKEN")
    if authtoken:
        ngrok.set_auth_token(authtoken)
    else:
        print("Warning: [FrontendServer] NGROK_AUTHTOKEN not set. Tunnel may be rate-limited.")
    
    public_url = ngrok.connect(8080)
    print(f"--- ✅ [FrontendServer] Public URL is LIVE: {public_url} ---")
    print("--- 🚀 [FrontendServer] Starting FastHTML UI Server on http://0.0.0.0:8080 ---")
    uvicorn.run(app, host="0.0.0.0", port=8080)
