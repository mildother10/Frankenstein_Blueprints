import os, yaml, json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from tools.web_tools import *
from tools.librarian_tools import *
from tools.rag_tools import *
from tools.quantum_tools import *

class ResearchGraphState(TypedDict):
    research_topic: str
    plan: str
    draft: str
    review: str
    final_report: str
    research_results: Dict[str, Any]
    messages: List 

class ResearchGraph:
    def __init__(self):
        print("Initializing ResearchGraph...")
        self.config_path = "config" # Relative path
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
            firecrawl_search_and_scrape,
            search_hf_models, get_hf_daily_papers, search_arxiv,
            search_oreilly, search_coursera, search_deeplearning_ai,
            search_dlai_knowledge_base,
            list_quantum_devices, run_quantum_circuit, check_quantum_job_status
        ]

    def load_configs(self):
        print("Loading agents.yaml and tasks.yaml...")
        with open(os.path.join(self.config_path, "agents.yaml"), 'r') as f:
            agents_config = yaml.safe_load(f)
        with open(os.path.join(self.config_path, "tasks.yaml"), 'r') as f:
            tasks_config = yaml.safe_load(f)
        return agents_config, tasks_config

    def create_agent_node(self, agent_name: str, system_prompt: str, tools: List):
        def agent_node(state: ResearchGraphState) -> Dict[str, Any]:
            print(f"--- 🧠 Executing Agent: {agent_name} ---")
            research_context = "\n\n".join(f"--- {t} ---\n{r}" for t, r in state['research_results'].items())
            task_config = self.tasks_config['tasks'][agent_name]
            task_prompt = task_config['prompt'].format(
                research_topic=state['research_topic'], research_context=research_context,
                plan=state.get('plan', ''), draft=state.get('draft', ''), review=state.get('review', '')
            )
            prompt = PromptTemplate.from_template(f"{system_prompt}\n\n{task_prompt}")
            llm_with_tools = self.llm.bind_tools(tools)
            chain = prompt | llm_with_tools
            llm_response = chain.invoke(state) 
            return {"messages": [llm_response]}
        return agent_node

    def create_tool_node(self):
        tool_map = {tool.name: tool for tool in self.all_tools}
        def tool_executor_node(state: ResearchGraphState) -> Dict[str, Any]:
            print("--- 🛠️ Executing Tool(s) ---")
            last_message = state["messages"][-1]
            tool_calls = last_message.tool_calls
            tool_outputs = []
            for call in tool_calls:
                tool_name = call['name']
                tool_args = call['args']
                if tool_name in tool_map:
                    try:
                        tool_function = tool_map[tool_name]
                        print(f"--- Calling: {tool_name}({tool_args}) ---")
                        output = tool_function.invoke(tool_args)
                        state['research_results'][tool_name] = str(output)
                        tool_outputs.append({"tool_call_id": call['id'], "output": str(output)})
                    except Exception as e:
                        tool_outputs.append({"tool_call_id": call['id'], "output": f"Error: {e}"})
                else:
                    tool_outputs.append({"tool_call_id": call['id'], "output": "Error: Tool not found."})
            print("--- ✅ Tool(s) Execution Complete ---")
            return {"messages": tool_outputs}
        return tool_executor_node

    def create_simple_agent_node(self, agent_name: str):
        def agent_node(state: ResearchGraphState) -> Dict[str, Any]:
            print(f"--- 🧠 Executing Agent: {agent_name} ---")
            system_prompt = self.agents_config['agents'][agent_name]['system_prompt']
            research_context = "\n\n".join(f"--- {t} ---\n{r}" for t, r in state['research_results'].items())
            task_config = self.tasks_config['tasks'][agent_name]
            task_prompt = task_config['prompt'].format(
                research_topic=state['research_topic'], research_context=research_context,
                plan=state.get('plan', ''), draft=state.get('draft', '') 
            )
            prompt = PromptTemplate.from_template(f"{system_prompt}\n\n{task_prompt}")
            chain = prompt | self.llm
            llm_response = chain.invoke(state)
            print(f"--- ✅ {agent_name} Complete ---")
            if agent_name == "Planner": return {"plan": llm_response}
            if agent_name == "Writer": return {"draft": llm_response}
            if agent_name == "Reviewer": return {"review": llm_response}
            return {} 
        return agent_node
        
    def compile_graph(self):
        print("Compiling graph...")
        workflow = StateGraph(ResearchGraphState)
        planner = self.create_simple_agent_node("Planner")
        researcher = self.create_agent_node("Researcher", self.agents_config['agents']['Researcher']['system_prompt'], self.all_tools)
        tool_node = self.create_tool_node()
        writer = self.create_simple_agent_node("Writer")
        reviewer = self.create_simple_agent_node("Reviewer")
        workflow.add_node("Planner", planner)
        workflow.add_node("Researcher", researcher)
        workflow.add_node("call_tools", tool_node)
        workflow.add_node("Writer", writer)
        workflow.add_node("Reviewer", reviewer)
        workflow.set_entry_point("Planner")
        workflow.add_edge("Planner", "Researcher")
        workflow.add_conditional_edges("Researcher",
            lambda state: "call_tools" if state["messages"][-1].tool_calls else "Writer",
            {"call_tools": "call_tools", "Writer": "Writer"})
        workflow.add_edge("call_tools", "Researcher")
        workflow.add_edge("Writer", "Reviewer")
        workflow.add_edge("Reviewer", END)
        compiled_graph = workflow.compile()
        print("✅ Graph Compiled.")
        return compiled_graph
