from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from services.rag import explain_code
from services.refactor import refactor_code
from services.codebase import analyze_codebase

app = FastAPI(title="CodeExplainer API")

# Setup CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to chrome-extension://<id>
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExplainRequest(BaseModel):
    code: str
    language: Optional[str] = "English"

class RefactorRequest(BaseModel):
    code: str
    language: Optional[str] = "English"

class CodebaseRequest(BaseModel):
    repo_path: str
    language: Optional[str] = "English"

@app.post("/explain")
async def explain_endpoint(req: ExplainRequest):
    print(f"DEBUG: Language received: {req.language}")
    try:
        explanation = explain_code(req.code, req.language)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refactor")
async def refactor_endpoint(req: RefactorRequest):
    try:
        result = refactor_code(req.code, req.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/codebase")
async def codebase_endpoint(req: CodebaseRequest):
    try:
        result = analyze_codebase(req.repo_path, req.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
