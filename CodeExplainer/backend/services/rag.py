import os
import chromadb
from chromadb.utils import embedding_functions
from utils.ai_client import generate_text

# Initialize ChromaDB client persisted
chroma_client = chromadb.Client()

# Setup embedding function explicitly (uses sentence-transformers)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="documentation", 
    embedding_function=sentence_transformer_ef
)

# dummy docs removed to prevent hallucinations

def explain_code(code: str, language: str = "English") -> str:
    """
    RAG pipeline:
    1. Query ChromaDB for top-2 docs related to the code.
    2. Build context and send to Gemini.
    """
    results = collection.query(
        query_texts=[code],
        n_results=2
    )
    
    context = ""
    # Only use context if it's statistically relevant (low distance)
    # ChromaDB distance: 0 is perfect match, >1.5 is usually irrelevant
    if results and results['documents'] and results['distances']:
        relevant_docs = []
        for i in range(len(results['documents'][0])):
            if results['distances'][0][i] < 1.2: # Tune this threshold
                relevant_docs.append(results['documents'][0][i])
        
        if relevant_docs:
            context = "\n".join(relevant_docs)
        
    # Special handling for Hinglish instructions
    lang_instruction = f"ALL OUTPUT MUST BE IN {language.upper()}."
    if language.lower() == "hinglish":
        lang_instruction = "Use HINGLISH (a mix of Hindi and English). Use Hindi for the logic and English for technical terms like 'loop', 'variable', 'function'. Write Hindi using English alphabet (Roman script)."

    prompt = f"""
CRITICAL: {lang_instruction}

You are a friendly teacher. Explain this code very simply for a beginner using {language}.
If using Hinglish, speak like a YouTuber explaining code to their students.

[CODE START]
{code}
[CODE END]

Simple Explanation (in {language}):
"""
    return generate_text(prompt)
