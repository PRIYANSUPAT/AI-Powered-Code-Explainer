chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeCode",
    title: "Analyze with CodeExplainer",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyzeCode") {
    chrome.storage.local.set({ selectedCode: info.selectionText }, () => {
      // The user will open the popup manually to see it
    });
  }
});
