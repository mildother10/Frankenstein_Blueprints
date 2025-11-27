import os, yaml, json, asyncio
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Union

# Import the *only* tool we need now
from tools.delegation_tools import delegate_to_5w1h_crews
from dotenv import load_dotenv

load_dotenv()

class DelegationResearchState(TypedDict):
    research_topic: str
    plan: str
    research_context: Dict[str, Any] # Stores the dict from the parallel tool
    draft: str
    messages: List 

class ResearchGraph:
    
    def __init__(self):
        print("Initializing ResearchGraph...")
        self.config_path = "config"
        self.llm = self.load_llm()
        self.all_tools = [delegate_to_5w1h_crews] # Only one tool
        self.agents_config, self.tasks_config = self.load_configs()
        self.graph = self.compile_graph()
        print("✅ ResearchGraph Initialized.")

    def load_llm(self):
        print("Loading Ollama LLM (mistral)...")
        return Ollama(model="mistral") 

    def load_configs(self):
        print("Loading agents.yaml and tasks.yaml...")
        with open(os.path.join(self.config_path, "agents.yaml"), 'r') as f:
            agents_config = yaml.safe_load(f)
        with open(os.path.join(self.config_path, "tasks.yaml"), 'r') as f:
            tasks_config = yaml.safe_load(f)
        return agents_config, tasks_config

    # --- NODES ARE NOW ASYNC DEFS ---

    async def run_agent_node(self, state: DelegationResearchState, agent_name: str, tools: List = []):
        """Async helper to run an agent node."""
        print(f"--- 🧠 Executing Agent: {agent_name} ---")
        
        system_prompt = self.agents_config['agents'][agent_name]['system_prompt']
        task_config = self.tasks_config['tasks'][agent_name]
        task_prompt = task_config['prompt'].format(
            research_topic=state['research_topic'], 
            plan=state.get('plan', 'N/A'),
            research_context=state.get('research_context', {})
        )
        
        prompt = PromptTemplate.from_template(f"{system_prompt}\n\n{task_prompt}")
        
        if tools:
            llm_with_tools = self.llm.bind_tools(tools)
            chain = prompt | llm_with_tools
            # Use .ainvoke() for async
            llm_response = await chain.ainvoke(state)
            return {"messages": [llm_response]}
        else:
            chain = prompt | self.llm
            # Use .ainvoke() for async
            llm_response = await chain.ainvoke(state)
            return {"draft": llm_response}

    async def run_tool_node(self, state: DelegationResearchState):
        """Async helper to run the parallel tool node."""
        print("--- 🛠️ Executing Parallel Delegation Tool ---")
        last_message = state["messages"][-1]
        tool_call = last_message.tool_calls[0] # We only have one tool
        
        # Call the async tool
        tool_output = await delegate_to_5w1h_crews.ainvoke(tool_call['args'])
        
        print("--- ✅ Parallel Delegation Complete ---")
        # Store results directly in the main context
        return {"research_context": tool_output, "messages": []}

    def compile_graph(self):
        print("Compiling graph (Parallel Microservice Flow)...")
        workflow = StateGraph(DelegationResearchState)
        
        # --- THE FINAL FIX: Define async nodes, not sync lambdas ---
        async def planner_node(state):
            return await self.run_agent_node(state, "Planner", self.all_tools)
            
        async def tool_node(state):
            return await self.run_tool_node(state)
            
        async def writer_node(state):
            return await self.run_agent_node(state, "Writer")

        workflow.add_node("Planner", planner_node)
        workflow.add_node("DelegationExecutor", tool_node)
        workflow.add_node("Writer", writer_node)

        # Build the simple, sequential graph
        workflow.set_entry_point("Planner")
        workflow.add_edge("Planner", "DelegationExecutor")
        workflow.add_edge("DelegationExecutor", "Writer")
        workflow.add_edge("Writer", END)
        
        compiled_graph = workflow.compile()
        print("✅ Graph Compiled.")
        return compiled_graph
