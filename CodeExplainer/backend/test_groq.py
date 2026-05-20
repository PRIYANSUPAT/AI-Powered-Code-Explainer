import os
from groq import Groq
from dotenv import load_dotenv

# Load from the correct absolute path to be sure
load_dotenv(dotenv_path="c:/Users/priya/OneDrive/Desktop/Minor Project/CodeExplainer/backend/.env")

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("FAILED: GROQ_API_KEY not found in .env")
    exit(1)

print(f"Testing with API Key: {API_KEY[:10]}...")

try:
    client = Groq(api_key=API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": "Explain what a recursion is in one sentence."}
        ],
    )
    print("SUCCESS! API is working.")
    print(f"Response: {completion.choices[0].message.content}")
except Exception as e:
    print(f"FAILED! Error: {str(e)}")
