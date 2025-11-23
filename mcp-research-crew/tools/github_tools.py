import os
from langchain_core.tools import tool
from github import Github, GithubException

# Initialize the Github object using the token from our .env file
try:
    github_client = Github(os.environ.get("GITHUB_TOKEN"))
except Exception as e:
    print(f"Warning: Could not initialize GitHub client. {e}")
    github_client = None

@tool("GitHub Repository Search Tool")
def search_github_repositories(query: str, top_k: int = 5) -> str:
    """
    Searches GitHub for repositories matching a query.
    Returns the top_k results with their name, description, and URL.
    """
    print(f"Tool: search_github_repositories (Query: {query})")
    if github_client is None:
        return "Error: GitHub client not initialized. Check GITHUB_TOKEN."
    
    try:
        repositories = github_client.search_repositories(query, sort="stars", order="desc")
        
        output = []
        for i, repo in enumerate(repositories):
            if i >= top_k:
                break
            output.append(
                f"- Repo: {repo.full_name}\n"
                f"  URL: {repo.html_url}\n"
                f"  Stars: {repo.stargazers_count}\n"
                f"  Description: {repo.description}\n"
            )
        
        if not output:
            return f"No GitHub repositories found for: {query}"
            
        return "\n".join(output)
    except GithubException as e:
        return f"Error searching GitHub: {e.payload}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
