# CodeExplainer AI - Local Setup Guide

Welcome to **CodeExplainer AI**! This guide will help you set up and run the entire system (Backend + Chrome Extension) on your local machine using VS Code.

---

## 1. Prerequisites
Before starting, ensure you have the following installed:
*   **Python 3.9+**
*   **Node.js & NPM** (Optional, but useful for extension testing)
*   **Google Chrome**
*   **VS Code**
*   **Groq API Key**: Get it from [console.groq.com](https://console.groq.com)

---

## 2. Project Structure
```text
CodeExplainer/
├── backend/            # FastAPI Server (Python)
│   ├── app.py          # Main entry point
│   ├── services/       # AI & RAG logic
│   └── .env            # API Keys
└── extension/          # Chrome Extension (HTML/JS)
```

---

## 3. Backend Setup (VS Code)

### Step 1: Open Folder
Open the `CodeExplainer/backend` folder in VS Code.

### Step 2: Create Virtual Environment
Open a terminal in VS Code (`Ctrl + ~`) and run:
```powershell
python -m venv venv
```

### Step 3: Activate Environment
*   **Windows**: `.\venv\Scripts\activate`
*   **Mac/Linux**: `source venv/bin/activate`

### Step 4: Install Dependencies
Run the following command to install all required libraries:
```powershell
pip install fastapi uvicorn groq chromadb sentence-transformers gitpython python-dotenv pydantic
```

### Step 5: Configure API Key
Inside the `backend/` folder, create a file named `.env` and add your Groq key:
```text
GROQ_API_KEY=your_actual_key_here
```

### Step 6: Start the Server
Run the backend server using Uvicorn:
```powershell
python -m uvicorn app:app --reload --port 8000
```
Status: The backend is now live at `http://localhost:8000`.

---

## 4. Chrome Extension Setup

### Step 1: Open Chrome
Go to the URL: `chrome://extensions/`

### Step 2: Enable Developer Mode
Turn on the **"Developer mode"** toggle in the top-right corner.

### Step 3: Load the Extension
Click **"Load unpacked"** and select the `CodeExplainer/extension` folder.

### Step 4: Pin to Toolbar
Click the Extensions (puzzle piece) icon in Chrome and **Pin** CodeExplainer AI.

---

## 5. Usage
1.  Ensure the **Backend Terminal** in VS Code is running.
2.  Open any website or local file in Chrome.
3.  Click the **CodeExplainer AI** icon.
4.  Paste your code, select a language, and click **EXECUTE ANALYSIS**.

---

## 6. Troubleshooting
*   **Connection Error**: Ensure the backend is running on port 8000. If you change the port, update the URL in `extension/popup.js`.
*   **Invalid API Key**: Check your `.env` file for typos.
*   **CORS Issues**: The `app.py` is configured to allow `*` origins, which works for local development.

---

**Happy Coding!** 🚀
