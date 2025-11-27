import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

# --- THIS IS THE REFACTOR ---
# We now import our robust, reusable helper function
from utils.scraping_utils import scrape_website
# --------------------------

@tool("O'Reilly Search Tool")
def search_oreilly(query: str) -> str:
    """
    Searches the O'Reilly learning platform for books and courses
    related to the query. Scrapes the top 3 results.
    """
    print(f"Tool: search_oreilly (Query: {query})")
    search_url = f"httpsfs://www.oreilly.com/search/?query={query}"
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('a', href=True, attrs={'data-testid': 'search-result-title-link'})
        if not results: return f"No O'Reilly results found for: {query}"
        output = []
        for res in results[:3]:
            title = res.get_text(strip=True)
            url = f"https"f"://www.oreilly.com{res['href']}"
            # --- SEE HOW CLEAN THIS IS? ---
            snippet = scrape_website(url) 
            output.append(f"- Title: {title}\n  URL: {url}\n  Snippet: {snippet}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Error searching O'Reilly: {e}"

@tool("Coursera Search Tool")
def search_coursera(query: str) -> str:
    """
    Searches Coursera for courses related to the query.
    Returns the top 3 results.
    """
    print(f"Tool: search_coursera (Query: {query})")
    search_url = f"httpsfs://www.coursera.org/search?query={query}"
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.select('main ul > li a[data-e2e="search-card-listing-title-link"]')
        if not results: return f"No Coursera results found for: {query}"
        output = [f"- Title: {r.get_text(strip=True)}\n  URL: https://www.coursera.org{r['href']}\n" for r in results[:3]]
        return "\n".join(output)
    except Exception as e:
        return f"Error searching Coursera: {e}"

@tool("DeepLearning.AI Search Tool")
def search_deeplearning_ai(query: str) -> str:
    """
    Searches DeepLearning.AI for courses and content
    related to the query. Returns the top 3 results.
    """
    print(f"Tool: search_deeplearning_ai (Query: {query})")
    search_url = f"httpsfs://www.deeplearning.ai/search/?s={query}"
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.select('h3.search-card__title a')
        if not results: return f"No DeepLearning.AI results found for: {query}"
        output = [f"- Title: {r.get_text(strip=True)}\n  URL: {r['href']}\n" for r in results[:3]]
        return "\n".join(output)
    except Exception as e:
        return f"Error searching DeepLearning.AI: {e}"
