import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is missing. Please set it in backend/.env")

client = Groq(api_key=API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"

def generate_text(prompt: str, temperature: float = 0.2) -> str:
    """
    Generate text using Groq API (Llama 3.1).
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=2048,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        raise e

def generate_json(prompt: str, temperature: float = 0.2) -> str:
    """
    Generate structured JSON output using Groq API.
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )
        text = completion.choices[0].message.content
        
        # Safety: remove potential markdown blocks if present
        if text.strip().startswith("```"):
            lines = text.strip().split("\n")
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        return text
    except Exception as e:
        print(f"Groq API JSON Error: {str(e)}")
        raise e
