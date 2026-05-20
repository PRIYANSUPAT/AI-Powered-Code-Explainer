import os
import ast
import json
import shutil
import tempfile
from typing import Dict, List, Any
from git import Repo
from utils.ai_client import generate_text

def analyze_codebase(repo_path: str, language: str = "English") -> Dict[str, Any]:
    """
    Analyzes a codebase. Supports:
    1. Local absolute/relative paths.
    2. GitHub repository URLs (clones them to a temp directory).
    """
    is_temp = False
    actual_path = repo_path

    # Check if it's a GitHub URL
    if repo_path.startswith("http") and "github.com" in repo_path:
        try:
            temp_dir = tempfile.mkdtemp(prefix="code_explainer_")
            print(f"Cloning {repo_path} to {temp_dir}...")
            Repo.clone_from(repo_path, temp_dir, depth=1)
            actual_path = temp_dir
            is_temp = True
        except Exception as e:
            return {"error": f"Failed to clone repository: {str(e)}"}
    else:
        # Local path handling
        actual_path = os.path.abspath(repo_path)
        if not os.path.exists(actual_path) or not os.path.isdir(actual_path):
            return {"error": f"Invalid repository path: {repo_path}. The path must point to an existing directory or a valid GitHub URL."}

    result = {
        "files": {},
        "dependency_graph": {},
        "entry_point": None,
        "summary": "",
        "readme_content": None
    }

    entry_point_candidates = []

    # Try to find and read README
    readme_files = ["README.md", "readme.md", "README", "readme.txt"]
    for rf in readme_files:
        rf_path = os.path.join(actual_path, rf)
        if os.path.exists(rf_path):
            try:
                with open(rf_path, 'r', encoding='utf-8') as f:
                    result["readme_content"] = f.read()[:5000] # Cap at 5000 chars for prompt
                break
            except:
                pass

    for root, dirs, files in os.walk(actual_path):
        # Ignore common hidden or virtualenv/dist directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env', 'node_modules', 'dist', 'build']]
        
        for file in files:
            # Analyze Python, JS, Java, C++ files
            if file.endswith(('.py', '.js', '.java', '.cpp', '.h', '.ts')):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, actual_path)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Detailed parsing for Python
                    if file.endswith('.py'):
                        try:
                            tree = ast.parse(content)
                            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                            result["files"][rel_path] = {"classes": classes, "functions": functions}
                            
                            if "if __name__ == '__main__':" in content or file in ["main.py", "app.py"]:
                                entry_point_candidates.append(rel_path)
                        except:
                            result["files"][rel_path] = {"summary": "Python file (parsing failed)"}
                    else:
                        # Basic recognition for other languages
                        result["files"][rel_path] = {"type": file.split('.')[-1], "size": len(content)}
                
                except Exception as e:
                    result["files"][rel_path] = {"error": f"Read failed: {str(e)}"}

    # Determine best entry point
    if "main.py" in entry_point_candidates:
        result["entry_point"] = "main.py"
    elif entry_point_candidates:
        result["entry_point"] = entry_point_candidates[0]
        
    # Special handling for Hinglish instructions
    lang_instruction = f"ALL OUTPUT MUST BE IN {language.upper()}."
    if language.lower() == "hinglish":
        lang_instruction = "Use HINGLISH (a mix of Hindi and English). Use Hindi for the logic and English for technical terms like 'loop', 'variable', 'function'. Write Hindi using English alphabet (Roman script)."

    # Generate summary using Groq (Llama 3.1)
    # Give priority to README if available
    summary_prompt = f"""
CRITICAL: {lang_instruction}

You are a project architect. Summarize this codebase in simple language using {language}.
README Content:
{result['readme_content'] or 'No README found.'}

Project Structure:
{json.dumps(list(result["files"].keys())[:50], indent=2)} (showing top 50 files)

Please explain:
1. What does this project do?
2. What is the tech stack?
3. How is it organized?
"""
    try:
        result["summary"] = generate_text(summary_prompt)
    except Exception as e:
        result["summary"] = f"Summary generation failed: {str(e)}"

    # Cleanup temp directory if we cloned
    if is_temp:
        try:
            shutil.rmtree(actual_path)
        except:
            pass
        
    return result
