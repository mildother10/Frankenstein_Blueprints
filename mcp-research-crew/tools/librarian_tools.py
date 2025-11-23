import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

def scrape_website(url: str) -> str:
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return f"Error: Failed to retrieve content from {url}"
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]): script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split()[:500])
    except Exception as e:
        return f"Error scraping {url}: {e}"

@tool("O'Reilly Search Tool")
def search_oreilly(query: str) -> str:
    """
    Searches the O'Reilly learning platform for books and courses
    related to the query. Scrapes the top 3 results.
    """
    print(f"Tool: search_oreilly (Query: {query})")
    search_url = f"https://www.oreilly.com/search/?query={query}"
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('a', href=True, attrs={'data-testid': 'search-result-title-link'})
        if not results: return f"No O'Reilly results found for: {query}"
        output = []
        for res in results[:3]:
            title = res.get_text(strip=True)
            url = f"https://www.oreilly.com{res['href']}"
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
    search_url = f"https://www.coursera.org/search?query={query}"
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
    search_url = f"https://www.deeplearning.ai/search/?s={query}"
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.select('h3.search-card__title a')
        if not results: return f"No DeepLearning.AI results found for: {query}"
        output = [f"- Title: {r.get_text(strip=True)}\n  URL: {r['href']}\n" for r in results[:3]]
        return "\n".join(output)
    except Exception as e:
        return f"Error searching DeepLearning.AI: {e}"
