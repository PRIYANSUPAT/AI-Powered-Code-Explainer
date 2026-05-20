import json
from utils.ai_client import generate_json

def refactor_code(code: str, language: str = "English") -> dict:
    """
    Sends the code to Gemini to receive a structured refactored object.
    """
    prompt = f"""
You are an expert software engineer. Review the following code.
Refactor the code for stability and performance.

Output Language: {language}
IMPORTANT: ALL keys like 'improvements' and 'complexity_changes' must contain text in {language}.

Output MUST be a valid JSON object matching this schema exactly:
{{
    "refactored_code": "code string here",
    "improvements": ["list of improvements in {language}"],
    "complexity_changes": "explanation in {language}"
}}

Code:
{code}
"""
    try:
        response_text = generate_json(prompt)
        # Gemini JSON mode sometimes wraps in ```json ... ``` despite mime_type
        # Let's clean it up just in case
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
            
        data = json.loads(response_text)
        return data
    except Exception as e:
        print(f"DEBUG: Raw response from model: {response_text}")
        return {"error": f"Failed to parse Gemini response: {str(e)}"}
