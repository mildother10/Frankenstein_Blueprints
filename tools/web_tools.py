import os
from firecrawl import FirecrawlApp
from langchain_core.tools import tool
from huggingface_hub import HfApi
from arxiv import Search, SortCriterion

@tool("Firecrawl Web Search & Scrape Tool")
def firecrawl_search_and_scrape(query: str) -> str:
    """
    Performs a web search for a given query using Firecrawl and
    then scrapes the content of the top result, returning it as
    clean, readable markdown. This is your primary tool for
    general web research.
    """
    print(f"Tool: firecrawl_search_and_scrape (Query: {query})")
    try:
        api_key = os.environ["FIRE_API_KEY"]
        app = FirecrawlApp(api_key=api_key)
        search_results = app.search(query, page_options={'page': 1, 'per_page': 3})
        if not search_results:
            return f"No search results found for query: {query}"
        top_url = search_results[0]['url']
        scraped_data = app.scrape_url(top_url, {'pageOptions': {'format': 'markdown'}})
        return scraped_data['markdown']
    except Exception as e:
        return f"Error running Firecrawl tool: {e}"

@tool("Hugging Face Model Search Tool")
def search_hf_models(task: str, top_k: int = 3) -> str:
    """
    Searches the Hugging Face Hub for models related to a specific
    task (e.g., 'text-generation', 'image-classification').
    """
    print(f"Tool: search_hf_models (Task: {task})")
    try:
        api = HfApi(token=os.environ.get("HUGGINGFACE_TOKEN"))
        models = api.list_models(filter=task, sort="downloads", direction=-1, limit=top_k)
        if not models: return f"No models found for task: {task}"
        results = [f"- Model ID: {m.modelId}, Downloads: {m.downloads}" for m in models]
        return "\n".join(results)
    except Exception as e:
        return f"Error searching Hugging Face models: {e}"

@tool("Hugging Face Daily Papers Tool")
def get_hf_daily_papers(query: str = None, top_k: int = 5) -> str:
    """
    Fetches the top_k most recent papers from the Hugging Face
    Daily Papers feed.
    """
    print(f"Tool: get_hf_daily_papers (Query: {query})")
    try:
        api = HfApi(token=os.environ.get("HUGGINGFACE_TOKEN")) 
        papers = api.list_models(model_type="dataset", search=query, tags="arxiv", sort="lastModified", direction=-1, limit=top_k)
        if not papers: return "No recent papers found on Hugging Face."
        results = [f"- Paper: {p.modelId}, URL: https://huggingface.co/datasets/{p.modelId}" for p in papers]
        return "\n".join(results)
    except Exception as e:
        return f"Error fetching Hugging Face papers: {e}"

@tool("ArXiv Academic Paper Search Tool")
def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Searches ArXiv for academic papers related to a query.
    """
    print(f"Tool: search_arxiv (Query: {query})")
    try:
        search = Search(query=query, max_results=max_results, sort_by=SortCriterion.Relevance)
        results = [f"- Title: {r.title}\n  URL: {r.entry_id}\n  Summary: {r.summary.strip()}" for r in search.results()]
        return "\n---\n".join(results) if results else f"No ArXiv papers found for query: {query}"
    except Exception as e:
        return f"Error searching ArXiv: {e}"
