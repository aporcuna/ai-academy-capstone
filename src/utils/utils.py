import os
from dotenv import load_dotenv

def getPatToken() -> str:
    """
    Retrieves the GitHub Personal Access Token from environment variables.
    Raises an error if the token is not set.
    """
    
    load_dotenv();
    github_token = os.getenv("GITHUB_PAT_TOKEN")
    if not github_token:
        raise ValueError("❌ ERROR: GITHUB_PAT_TOKEN no está definido en el archivo .env")

    return github_token