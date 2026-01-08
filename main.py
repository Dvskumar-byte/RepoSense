import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import app_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    repo_url: str

class ChatRequest(BaseModel):
    repo_url: str
    question: str

# This stores the REAL file list for each repo you analyze
REPO_CACHE = {}

def extract_repo_path(url: str):
    """Converts a GitHub URL into 'owner/repo' format."""
    path = url.replace("https://github.com/", "").strip("/")
    parts = path.split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return path

@app.post("/analyze")
async def analyze_repo(req: AnalyzeRequest):
    repo_path = extract_repo_path(req.repo_url)
    github_api_url = f"https://api.github.com/repos/{repo_path}/contents"
    
    async with httpx.AsyncClient() as client:
        # We add a User-Agent header which GitHub API requires
        response = await client.get(github_api_url, headers={"User-Agent": "Repo-Analyzer"})
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Could not find GitHub repository.")
        
        repo_contents = response.json()

    # Get real file/folder names
    real_files = []
    for item in repo_contents:
        real_files.append({
            "path": item["name"],
            "type": "blob" if item["type"] == "file" else "tree"
        })

    # Update the cache so the Chat knows the REAL files
    REPO_CACHE[req.repo_url] = [f["path"] for f in real_files]
    
    return {
        "status": "success",
        "files": real_files,
        "repo_path": repo_path
    }

@app.post("/chat")
async def chat_repo(req: ChatRequest):
    # Get the real file list we just fetched
    files = REPO_CACHE.get(req.repo_url, [])
    file_context = ", ".join(files) if files else "No file list available."
    
    inputs = {
        "repo_url": req.repo_url,
        "question": req.question,
        "context": file_context
    }
    
    result = app_graph.invoke(inputs)
    return {"answer": result["answer"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)