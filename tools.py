import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"
HEADERS = {}

if os.getenv("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"

def get_repo_info(owner, repo):
    return requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=HEADERS).json()

def get_repo_tree(owner, repo, branch):
    return requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=HEADERS
    ).json()

def get_file_content(owner, repo, path):
    res = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
        headers=HEADERS
    ).json()

    if "content" in res:
        return base64.b64decode(res["content"]).decode("utf-8", errors="ignore")
    return ""
