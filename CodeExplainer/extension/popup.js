const API_BASE = "http://localhost:8000";

let currentTab = "explain";

document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab-btn");
  const codeInputSection = document.getElementById("code-input-section");
  const codebaseInputSection = document.getElementById("codebase-input-section");
  const codeInput = document.getElementById("code-input");
  
  // Try to load selection from matching context menu or active tab
  try {
    chrome.storage.local.get(["selectedCode"], (res) => {
      if (res.selectedCode) {
        codeInput.value = res.selectedCode;
        chrome.storage.local.remove(["selectedCode"]);
      } else {
        // get selection from active tab
        chrome.tabs.query({active: true, currentWindow: true}, function(activeTabs) {
          if(activeTabs.length > 0) {
            chrome.tabs.sendMessage(activeTabs[0].id, {action: "getSelection"}, function(response) {
              if(response && response.text) {
                codeInput.value = response.text;
              }
            });
          }
        });
      }
    });
  } catch (e) {
    console.log("Chrome API not available outside extension context.");
  }

  // Tab switching logic
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentTab = tab.dataset.tab;

      if (currentTab === "codebase") {
        codeInputSection.style.display = "none";
        codebaseInputSection.style.display = "block";
      } else {
        codeInputSection.style.display = "block";
        codebaseInputSection.style.display = "none";
      }
      
      clearResult();
    });
  });

  document.getElementById("action-btn").addEventListener("click", handleCodeAction);
  document.getElementById("analyze-repo-btn").addEventListener("click", handleCodebaseAction);
});

function clearResult() {
  document.getElementById("result").innerHTML = "";
  document.getElementById("result").className = "result-box";
}

function showLoader() {
  document.getElementById("loader").style.display = "block";
  document.getElementById("result").style.display = "none";
}

function hideLoader() {
  document.getElementById("loader").style.display = "none";
  document.getElementById("result").style.display = "block";
}

function displayError(err) {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = `<span class="error">Error: ${err}</span>`;
  hideLoader();
}

async function handleCodeAction() {
  const code = document.getElementById("code-input").value;
  const langDropdown = document.getElementById("language-select");
  const language = langDropdown ? langDropdown.value : "English";
  
  if (!code.trim()) return alert("Please provide some code.");

  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = `<small style="color: blue">Targeting Language: ${language}...</small>`;
  resultDiv.style.display = "block";
  
  showLoader();
  try {
    const res = await fetch(`${API_BASE}/${currentTab}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language })
    });
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.detail || "Server error");
    
    const resultDiv = document.getElementById("result");
    if (currentTab === "explain") {
      resultDiv.innerHTML = `<strong>Explanation:</strong><br><pre>${data.explanation}</pre>`;
    } else if (currentTab === "refactor") {
      if(data.error) throw new Error(data.error);
      
      let html = `<strong>Refactored Code:</strong><pre>${data.refactored_code}</pre>`;
      html += `<strong>Improvements:</strong><ul>`;
      if(data.improvements && Array.isArray(data.improvements)){
          data.improvements.forEach(imp => { html += `<li>${imp}</li>`; });
      }
      html += `</ul>`;
      html += `<strong>Complexity changes:</strong><p>${data.complexity_changes}</p>`;
      resultDiv.innerHTML = html;
    }
  } catch (err) {
    displayError(err.message);
  } finally {
    hideLoader();
  }
}

async function handleCodebaseAction() {
  const repo_path = document.getElementById("repo-path").value;
  const langDropdown = document.getElementById("language-select");
  const language = langDropdown ? langDropdown.value : "English";
  
  if (!repo_path.trim()) return alert("Please provide a repo path.");

  showLoader();
  try {
    const res = await fetch(`${API_BASE}/codebase`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_path, language })
    });
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.detail || "Server error");
    if (data.error) throw new Error(data.error);
    
    const resultDiv = document.getElementById("result");
    let html = `<strong>Summary:</strong><pre>${data.summary}</pre>`;
    html += `<strong>Entry Point:</strong> ${data.entry_point || 'Not detected'}<br><br>`;
    html += `<strong>Architecture Details:</strong><br>`;
    html += `<pre>${JSON.stringify(data.files, null, 2)}</pre>`;
    
    resultDiv.innerHTML = html;
  } catch (err) {
    displayError(err.message);
  } finally {
    hideLoader();
  }
}
