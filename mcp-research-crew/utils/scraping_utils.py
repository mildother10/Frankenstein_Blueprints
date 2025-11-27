import requests
from bs4 import BeautifulSoup

def scrape_website(url: str) -> str:
    """
    A helper function to scrape text content from a URL.
    This is not an agent tool.
    """
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
