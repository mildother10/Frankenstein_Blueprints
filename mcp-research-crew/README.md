# 🤖 Quantum-Validated MCP Research Crew (Microservice Arch)

_A 10-service parallel AI research agent built "The Hard Way."_

This is not a simple Python script; it is a **prototype for a massively scalable, parallel-processing AI research engine.**

At its core, this project uses a `langgraph` "Delegator" agent (`backend.1`) to receive a single research topic. It then fans out that topic to **6 specialist CrewAI microservices** (Who, What, When, Where, How, Why), which run in parallel. A final "Writer" agent synthesizes their findings into a single, comprehensive report.

---

## 🏗️ The 10-Service "Factory" Architecture

This project is built on a decoupled microservice architecture, managed by `honcho`. Each component runs in its own process, communicating over a local `http://localhost` network.



* **The Brain (Port 8000):** `backend_server.py`
    * The main FastAPI server that runs the `langgraph` "Delegator" and "Writer" agents. It receives user requests and orchestrates the entire workflow.
* **The UI (Port 8080):** `frontend_server.py`
    * A simple, streaming FastHTML UI for submitting research topics.
* **The 6 Workers (Ports 8001-8006):**
    * `who_crew_service.py` (Port 8001)
    * `what_crew_service.py` (Port 8002)
    * `when_crew_service.py` (Port 8003)
    * `where_crew_service.py` (Port 8004)
    * `how_crew_service.py` (Port 8005)
    * `why_crew_service.py` (Port 8006)
* **The Specialists (Ports 9000 & 9090):**
    * `quantum_server.py` (Port 9000): A placeholder service for future quantum-validation tools.
    * `code_executor_server.py` (Port 9090): A secure service for running generated code (currently a placeholder).

---

## 🛠️ Core Tech Stack

* **Orchestration:** `langgraph` (for the main "Delegator" graph)
* **Agents:** `crewai` (for the 6 specialist "Worker" crews)
* **Servers:** `fastapi` & `uvicorn` (for all 10 microservices)
* **Process Manager:** `honcho` (to run all 10 services at once)
* **Package Management:** `uv` (for high-speed, safe dependency resolution)
* **LLM:** `Ollama (mistral)` (for local, CPU-based inference)
* **Vector DB:** `chromadb` (for the RAG knowledge base)

---

## 🧟 The "Hard Way": A Developer's Saga

This project is a "Frankenstein's monster," and it was built with a philosophy of "brute force, hard-headed" tenacity. It is a testament to first-principles debugging.

This architecture is the result of winning a series of "Boss Fights" against modern AI development complexity:

1.  **Dependency Hell (Boss 1):** We fought and won a multi-front war between `pip`, `uv`, `fastapi`, `crewai`, and `langgraph`. The core conflict was a mathematical impossibility: `langgraph` requires `langchain-core>=0.2.0`, while older `crewai` versions required `langchain-core<0.2.0`.
    * **The Fix:** A "Hulk Smash" of `requirements.txt`, unpinning `crewai` and letting `uv`'s high-speed resolver find the *one* compatible modern version (`crewai==0.60.0`) that worked with `langgraph`.

2.  **The Environment Boss (Boss 2):** After solving the logic, `uv` failed with `No space left on device`.
    * **The Fix:** We diagnosed that `sentence-transformers` was pulling the full, multi-gigabyte `torch` library with CUDA files. We "Hulk Smashed" the `requirements.txt` again, adding `--extra-index-url` to force the lightweight, **CPU-only** build of `torch`, which fit on the free tier.

3.  **The "Database Ghost" (Boss 3):** After downgrading `chromadb` (from v0.5.x to v0.4.x) to solve a `crewai` conflict, the server was haunted by `sqlite3.OperationalError: no such column: collections.topic`.
    * **The Fix:** The new library was trying to read the *old* database file. We had to perform a "Final Exorcism" by running **5 separate `rm -rf` commands** to delete the "ghost" database from every possible hiding place (`chroma_db_dlai/`, `~/.chroma`, `chroma.sqlite3`, `chromadb/`, and the final culprit: `.chroma`).

4.  **The "Async Deadlock" (Final Boss):** With all 10 services running, the app would hang for 15+ minutes. This was not the CPU; it was a logic bug.
    * **The Fix:** The `async` FastAPI server was calling the `async` LangGraph with a *synchronous* `.invoke()` command, creating a fatal deadlock. We "Hulk Smashed" `backend_server.py` to use `async def` and `.ainvoke()`, finally breaking the "ghost in the machine."

---

## 🚦 Current Status & Bottlenecks

The 10-service architecture is **LIVE and FUNCTIONAL**.

The primary bottleneck is **not** a bug; it's a hardware limitation we call the **"Ollama Hang."**

* **The Problem:** The first time you send a query, the `backend.1` "Planner" node calls the `mistral` LLM. `Ollama` must load this multi-gigabyte model into the Codespace's RAM, which (on a CPU) can take **2-5 minutes**.
* **The Effect:** Your first query will feel "stuck" for several minutes. This is normal.
* **The Solution:** After the first run, the model is "hot" (loaded in memory), and subsequent queries will be much faster (though still CPU-bound). The *real* fix is outlined in the roadmap.

---

## 🗺️ Future Roadmap (The "Grand Plan 2.0")

This prototype is the foundation for a professional, cloud-native application.

1.  **Cloud GPU (The Speed Fix):** Migrate the 10-service architecture to a cloud provider (AWS, GCP, Azure) with a **GPU**. This will solve the "Ollama Hang," reducing model load time from minutes to seconds.
2.  **Pluggable Brains (The Power Fix):** Get an OpenAI API key and swap the LLM "brain" in `crew_runner.py` with a simple, one-line code change:
    * **From:** `return Ollama(model="mistral")`
    * **To:** `return ChatOpenAI(model="gpt-4-turbo")`
3.  **Serverless Deployment (The Scalability Fix):** Break down each of the 10 services into its own **Docker container** and deploy them as **Serverless Functions** (e.g., AWS Lambda). This way, they "spin up" on demand and "spin down to zero," reducing cost and latency.
4.  **The Avatar Interface (The "Human-in-the-Loop" Fix):**
    * Replace `frontend_server.py` with `pipecat_server.py`.
    * Use **Pipecat** to handle real-time audio streaming.
    * Use **Deepgram** for Speech-to-Text.
    * Use **HeyGen** to create a live, animated avatar.
    * Use **OpenAI TTS** for realistic Text-to-Speech.
    * This new server will act as the true "cockpit," allowing the user to *talk* to the research engine.

---

## 🚀 How to Run

1.  **Install Dependencies:**
    ```bash
    uv pip install -r requirements.txt --system
    ```
2.  **(First Time Only) Exorcise Ghosts:**
    * Run this sequence to ensure no old database files are hiding.
    ```bash
    rm -rf chroma_db_dlai
    rm -rf ~/.chroma
    rm -f chroma.sqlite3
    rm -rf chromadb
    rm -rf .chroma
    ```
3.  **Launch the 10-Service Architecture:**
    ```bash
    honcho start
    ```
4.  **Wait for Launch:** Wait about 15-30 seconds for all 10 services to start and their ports to open.
5.  **Access the UI:** Click the "Ports" tab in your Codespace and open the "Frontend (8080)" URL in a new browser tab.
6.  **Run Your First Query:** Submit your first query and **be patient**. Wait 2-5 minutes for the "Ollama Hang" (model load) to complete. You will see the logs come alive in your `honcho` terminal once it's done.
