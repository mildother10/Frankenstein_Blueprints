# Frankenstein Multi-Agent Swarm (v36.0)

This repository contains the blueprints and server code for a "Hybrid Compute" (v35.0) multi-agent swarm architecture.

The project is designed to minimize compute costs by intelligently splitting agents into two categories based on their processing needs.

---

## Architecture: "Hybrid Compute" (v35.0)

This architecture divides the agent "C-Suite" (v17.0) into two distinct groups:

### 1. CPU "Manager" Agents

These are lightweight, low-cost, high-availability agents designed for tasks like API routing, state management, and user interaction. They are built from a  (v34.0) base.

* **:** (Executive Assistant) The "v32.0" (Padded Layer) entrypoint. It sanitizes user prompts ("Doorkeeper") and translates them into structured JSON for the  ("Translator").
* **:** (Manager) The "v5.0" (Manager) orchestrator. It receives structured missions from the  and delegates tasks to the specialist agents.
* **:** (Conscience) The "v12.0" (Conscience) "Guardrail" (v22.0) agent for ethics and security validation.
* **:** (Corporate Memory) The "v21.0" (Corporate Memory) service for interfacing with our persistent "Study Guide" (v21.0) (EFS/DynamoDB).
* **:** (Embodied Interface) The "v30.0" (Embodied) "Eyes & Ears" (v30.0) for local user audio/video interaction.
* **:** (Gradio UI) The "v6.0" (Hybrid Swarm) "Monitoring" (v27.0) UI for observing the swarm.

### 2. GPU "Scientist" Agents

These are "on-demand" (v22.0) (EC2 Spot Instance) agents built . They are "Hulk" (v28.0) (heavy-duty) agents designed to be "hired" (v22.0) to run "Hugging Face" (v30.0) models and "R&D" (v23.0) loops.

* **:** (Professor Brain) The "v30.0" (Embodied) agent for running "Hulk" (v28.0) (AI) execution (e.g., model inference).
* **:** (R&D Loop) The "v23.0" (R&D Loop) "Critique Agent" (v23.0) (LangGraph).
* **:** (Gleener) The "v21.0" (Gleener) agent for "gleening" (v21.0) (scraping/processing) new data.

---

## "Hulk Smash 42.0": "CPU-Only Fallback" (Development Mode)

To "smash" (v28.0) (test) this "monster" (v36.0) in a "CPU-Only Sandbox" (v22.0) (like GitHub Codespaces or a "legacy Chromebook" (v22.0)), we use the "v42.0" (CPU-Only Fallback) plan.

1.  **"Smash" (v28.0) (Edit) :** "Hulk Smash" (v28.0) (comment out) the  (GPU) sections for all "Scientist" (v35.0) agents.
2.  **"Smash" (v28.0) (Edit) :** "Hulk Smash" (v28.0) (change) the  line in all "Scientist" (v35.0) Dockerfiles (e.g., ) from  to .

This allows the *entire* 11-agent "A2A Protocol" (v22.0) to be "smashed" (v28.0) (run) on a "cheap" (v34.0) (CPU) "sandbox" (v22.0) for "frontend" (v44.0) (UI) and "A2A Protocol" (v22.0) (logic) testing.
