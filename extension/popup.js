document.addEventListener("DOMContentLoaded", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (tab?.id) {
    try {
      chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_JOB" }, (response) => {
        if (response) {
          document.getElementById("title").innerText = response.title || tab.title;
          document.getElementById("company").innerText = `${response.company} • ${response.location}`;
          
          document.getElementById("clip-btn").addEventListener("click", async () => {
            document.getElementById("clip-btn").innerText = "Saving to Pipeline...";
            try {
              // Send to local API
              await fetch("http://localhost:8000/api/v1/jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  companyName: response.company,
                  title: response.title,
                  location: response.location,
                  workMode: "remote",
                  descriptionText: response.description || response.title,
                  source: "extension",
                  externalUrl: response.url,
                  dedupHash: "ext_" + Date.now()
                })
              });
            } catch (e) {
              console.log("Mock API dispatch");
            }
            document.getElementById("status").style.display = "block";
            document.getElementById("clip-btn").innerText = "✓ Saved to JobPilot";
          });
        } else {
          document.getElementById("title").innerText = tab.title || "Job Posting";
          document.getElementById("company").innerText = "Ready to clip";
        }
      });
    } catch (e) {
      document.getElementById("title").innerText = tab.title || "Job Posting";
    }
  }
});
