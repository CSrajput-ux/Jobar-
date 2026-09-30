// JobPilot Content Script for LinkedIn, Indeed, and Glassdoor
function extractJobDetails() {
  const url = window.location.href;
  let title = "";
  let company = "";
  let location = "";
  let description = "";

  if (url.includes("linkedin.com")) {
    title = document.querySelector(".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title")?.innerText?.trim() || "";
    company = document.querySelector(".job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name")?.innerText?.trim() || "";
    location = document.querySelector(".job-details-jobs-unified-top-card__primary-description-container")?.innerText?.trim() || "Remote";
    description = document.querySelector("#job-details, .jobs-description__content")?.innerText?.trim() || "";
  } else if (url.includes("indeed.com")) {
    title = document.querySelector("[data-testid='simpler-jobTitle'], h1.jobsearch-JobInfoHeader-title")?.innerText?.trim() || "";
    company = document.querySelector("[data-testid='inlineHeader-companyName']")?.innerText?.trim() || "";
    location = document.querySelector("[data-testid='inlineHeader-companyLocation']")?.innerText?.trim() || "Remote";
    description = document.querySelector("#jobDescriptionText")?.innerText?.trim() || "";
  } else {
    title = document.querySelector("h1")?.innerText?.trim() || "";
    company = document.querySelector("[data-test='employer-name']")?.innerText?.trim() || "";
    description = document.querySelector(".jobDescriptionContent")?.innerText?.trim() || "";
  }

  return {
    title: title || document.title,
    company: company || "Discovered Company",
    location: location || "Remote",
    description: description.slice(0, 5000),
    url: window.location.href,
    source: "extension"
  };
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "EXTRACT_JOB") {
    const job = extractJobDetails();
    sendResponse(job);
  }
});
