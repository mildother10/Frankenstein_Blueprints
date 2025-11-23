import os, yaml, json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Union

from tools.web_tools import *
from tools.librarian_tools import *
from tools.rag_tools import *
from tools.quantum_tools import *
from tools.github_tools import *
from tools.code_execution_tools import *
from dotenv import load_dotenv

load_dotenv()

class ConcurrentResearchState(TypedDict):
    research_topic: str
    plan: str
    draft: str
    review: str
    final_report: str
    research_results: Dict[str, Union[str, Dict]]
    messages: List 

class ResearchGraph:
    
    def __init__(self):
        print("Initializing ResearchGraph...")
        self.config_path = "config"
        self.llm = self.load_llm()
        self.all_tools = self.load_tools()
        self.agents_config, self.tasks_config = self.load_configs()
        self.graph = self.compile_graph()
        print("✅ ResearchGraph Initialized.")

    def load_llm(self):
        print("Loading Ollama LLM (llama3)...")
        return Ollama(model="llama3")

    def load_tools(self):
        print("Loading all tools...")
        return [
            firecrawl_search_and_scrape, search_hf_models, get_hf_daily_papers, search_arxiv,
            search_oreilly, search_coursera, search_deeplearning_ai,
            search_dlai_knowledge_base,
            list_quantum_devices, run_quantum_circuit, check_quantum_job_status,
            search_github_repositories,
            execute_python_code
        ]

    def load_configs(self):
        print("Loading agents.yaml and tasks.yaml...")
        with open(os.path.join(self.config_path, "agents.yaml"), 'r') as f:
            agents_config = yaml.safe_load(f)
        with open(os.path.join(self.config_path, "tasks.yaml"), 'r') as f:
            tasks_config = yaml.safe_load(f)
        return agents_config, tasks_config

    def create_tool_node(self):
        tool_map = {tool.name: tool for tool in self.all_tools}
        def tool_executor_node(state: ConcurrentResearchState) -> Dict[str, Any]:
            print(f"--- 🛠️ Executing Tool(s) for Agent: {state['caller_agent']} ---")
            last_message = state["messages"][-1]
            tool_calls = last_message.tool_calls
            tool_outputs = []
            
            agent_name = state.get('caller_agent')
            if not agent_name or not isinstance(state['research_results'], dict):
                 raise ValueError("Tool executor called without proper state context (caller_agent or research_results).")
            
            if agent_name not in state['research_results']:
                 state['research_results'][agent_name] = {}
            
            for call in tool_calls:
                tool_name = call['name']
                tool_args = call['args']
                if tool_name in tool_map:
                    try:
                        tool_function = tool_map[tool_name]
                        print(f"--- Calling: {tool_name}({tool_args}) ---")
                        output = tool_function.invoke(tool_args)
                        state['research_results'][agent_name][tool_name] = str(output)
                        tool_outputs.append({"tool_call_id": call['id'], "output": str(output)})
                    except Exception as e:
                        tool_outputs.append({"tool_call_id": call['id'], "output": f"Error: {e}"})
                else:
                    tool_outputs.append({"tool_call_id": call['id'], "output": "Error: Tool not found."})
            
            print("--- ✅ Tool(s) Execution Complete ---")
            return {"messages": tool_outputs, "caller_agent": agent_name}
        return tool_executor_node

    def create_5w1h_agent_node(self, agent_name: str, tools: List):
        system_prompt = self.agents_config['agents'][agent_name]['system_prompt']
        
        def agent_node(state: ConcurrentResearchState) -> Dict[str, Any]:
            print(f"--- 🧠 Executing Specialized Agent: {agent_name} ---")
            
            agent_context = state['research_results'].get(agent_name, {})
            research_context = "\n\n".join(f"--- {t} ---\n{r}" for t, r in agent_context.items())
            
            task_config = self.tasks_config['tasks'][agent_name]
            task_prompt = task_config['prompt'].format(
                research_topic=state['research_topic'], plan=state.get('plan', '')
            )
            
            prompt = PromptTemplate.from_template(f"{system_prompt}\n\nPLAN:\n{state['plan']}\n\nPREVIOUS CONTEXT:\n{research_context}\n\n{task_prompt}")
            llm_with_tools = self.llm.bind_tools(tools)
            chain = prompt | llm_with_tools
            llm_response = chain.invoke(state) 
            
            return {"messages": [llm_response], "caller_agent": agent_name}
        return agent_node

    def create_simple_agent_node(self, agent_name: str):
        system_prompt = self.agents_config['agents'][agent_name]['system_prompt']
        
        def agent_node(state: ConcurrentResearchState) -> Dict[str, Any]:
            print(f"--- 🧠 Executing Agent: {agent_name} ---")
            
            if agent_name == "Researcher":
                concurrent_results = ""
                for agent, tool_data in state['research_results'].items():
                    if isinstance(tool_data, dict):
                        concurrent_results += f"\n\n----- {agent} Findings -----\n"
                        for tool, output in tool_data.items():
                            concurrent_results += f"Source ({tool}):\n{output}\n\n"
            else:
                concurrent_results = state['research_results']

            task_config = self.tasks_config['tasks'][agent_name]
            task_prompt = task_config['prompt'].format(
                research_topic=state['research_topic'], research_context=concurrent_results,
                plan=state.get('plan', ''), draft=state.get('draft', '') 
            )
            
            prompt = PromptTemplate.from_template(f"{system_prompt}\n\n{task_prompt}")
            chain = prompt | self.llm
            llm_response = chain.invoke(state)
            
            print(f"--- ✅ {agent_name} Complete ---")
            if agent_name == "Planner": return {"plan": llm_response, "research_results": {}}
            if agent_name == "Researcher": return {"research_results": llm_response}
            if agent_name == "Writer": return {"draft": llm_response}
            if agent_name == "Reviewer": return {"review": llm_response}
            return {} 
        return agent_node

    def should_continue_research(state: ConcurrentResearchState):
        return "call_tools" if state["messages"][-1].tool_calls else "synthesize"
    
    # --- JUNCTION NODE: RETURNS A DICT WHERE KEYS ARE TARGET NODES ---
    def route_to_all_agents(state: ConcurrentResearchState):
        """
        Returns a dictionary mapping the state to the six parallel agent nodes.
        This is the method used by the Conditional Edge to trigger parallel execution.
        """
        return {
            "WhoAgent": state, "WhatAgent": state, "WhenAgent": state, 
            "WhereAgent": state, "HowAgent": state, "WhyAgent": state
        }


    def compile_graph(self):
        print("Compiling graph...")
        workflow = StateGraph(ConcurrentResearchState)
        
        # 1. Sequential Nodes
        planner = self.create_simple_agent_node("Planner")
        coordinator = self.create_simple_agent_node("Researcher")
        writer = self.create_simple_agent_node("Writer")
        reviewer = self.create_simple_agent_node("Reviewer")
        
        workflow.add_node("Planner", planner)
        workflow.add_node("CoordinatorSynthesize", coordinator)
        workflow.add_node("Writer", writer)
        workflow.add_node("Reviewer", reviewer)

        # 2. Parallel 5W1H Nodes (The Agents)
        parallel_nodes = ["WhoAgent", "WhatAgent", "WhenAgent", "WhereAgent", "HowAgent", "WhyAgent"]
        
        for agent_name in parallel_nodes:
            # Add Agent Node
            agent_node_func = self.create_5w1h_agent_node(agent_name, self.all_tools)
            workflow.add_node(agent_name, agent_node_func)
            
            # Add Tool Executor Node
            tool_executor_name = f"{agent_name}_ToolExecutor"
            tool_executor_node_func = self.create_tool_node()
            workflow.add_node(tool_executor_name, tool_executor_node_func)
            
            # Define loop edges for each agent
            workflow.add_conditional_edges(
                agent_name,
                self.should_continue_research,
                {"call_tools": tool_executor_name, "synthesize": "CoordinatorSynthesize"}
            )
            workflow.add_edge(tool_executor_name, agent_name)

        # --- EDGES ---
        # 1. Planner -> Parallel Agents (Fan Out - FIX: Use conditional routing)
        workflow.add_conditional_edges(
            "Planner",
            self.route_to_all_agents,
            # The branch mapping keys MUST match the function's return keys.
            {"WhoAgent": "WhoAgent", "WhatAgent": "WhatAgent", "WhenAgent": "WhenAgent", 
             "WhereAgent": "WhereAgent", "HowAgent": "HowAgent", "WhyAgent": "WhyAgent"}
        )
        
        # 2. Coordinator Synthesize -> Writer (This is the Fan-In point where all 6 converge)
        workflow.add_edge("CoordinatorSynthesize", "Writer")
        
        # 3. Final Output Nodes
        workflow.add_edge("Writer", "Reviewer")
        workflow.add_edge("Reviewer", END)

        # Set Start/End
        workflow.set_entry_point("Planner")
        
        compiled_graph = workflow.compile()
        print("✅ Graph Compiled.")
        return compiled_graph
