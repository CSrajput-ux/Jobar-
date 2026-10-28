const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[API] Remote call failed to ${url}, fallback to mock response:`, err);
    throw err;
  }
}

async function uploadForm<T>(url: string, form: FormData): Promise<T> {
  const res = await fetch(url, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message || body?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Profile & Onboarding
  getProfile: () => fetchJson<any>(`${API_BASE}/profile`),
  updateProfile: (data: any) => fetchJson<any>(`${API_BASE}/profile`, { method: "PUT", body: JSON.stringify(data) }),
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return uploadForm<any>(`${API_BASE}/profile/upload-cv`, form);
  },
  analyzeResumeMatches: () => fetchJson<any>(`${API_BASE}/profile/analyze-and-queue?queue_for_approval=true`, { method: "POST" }),
  getPreferences: () => fetchJson<any>(`${API_BASE}/profile/preferences`),
  updatePreferences: (data: any) => fetchJson<any>(`${API_BASE}/profile/preferences`, { method: "PUT", body: JSON.stringify(data) }),
  getCommonQA: () => fetchJson<any>(`${API_BASE}/profile/common-qa`),

  // Jobs
  getJobs: (params?: string) => fetchJson<any[]>(`${API_BASE}/jobs${params ? `?${params}` : ""}`),
  syncJobs: () => fetchJson<any>(`${API_BASE}/jobs/sync`, { method: "POST" }),
  getJob: (id: string) => fetchJson<any>(`${API_BASE}/jobs/${id}`),

  // Matches & Tailoring
  getMatch: (jobId: string) => fetchJson<any>(`${API_BASE}/matches/${jobId}`),
  tailorResume: (jobId: string) => fetchJson<any>(`${API_BASE}/matches/tailor-resume/${jobId}`, { method: "POST" }),

  // Applications
  getApplications: () => fetchJson<any[]>(`${API_BASE}/applications`),
  createApplication: (jobId: string, status?: string) => 
    fetchJson<any>(`${API_BASE}/applications`, { method: "POST", body: JSON.stringify({ jobId, status }) }),
  approveApplication: (appId: string) => 
    fetchJson<any>(`${API_BASE}/applications/${appId}/approve`, { method: "POST" }),
  updateApplicationStage: (appId: string, status: string) => 
    fetchJson<any>(`${API_BASE}/applications/${appId}`, { method: "PATCH", body: JSON.stringify({ status }) }),

  // Outreach & Contacts
  getContacts: () => fetchJson<any[]>(`${API_BASE}/outreach/contacts`),
  getEmails: () => fetchJson<any[]>(`${API_BASE}/outreach/emails`),
  generateEmail: (contactId: string, jobId: string, tone: string) => 
    fetchJson<any>(`${API_BASE}/outreach/generate`, { method: "POST", body: JSON.stringify({ contactId, jobId, tone }) }),
  sendEmail: (emailId: string) => 
    fetchJson<any>(`${API_BASE}/outreach/send/${emailId}`, { method: "POST" }),

  // Inbox
  getThreads: () => fetchJson<any[]>(`${API_BASE}/inbox/threads`),
  replyThread: (threadId: string, replyText: string) => 
    fetchJson<any>(`${API_BASE}/inbox/threads/${threadId}/reply`, { method: "POST", body: JSON.stringify({ reply_text: replyText }) }),

  // Calendar
  getCalendarEvents: () => fetchJson<any[]>(`${API_BASE}/calendar/events`),
  proposeSlots: () => fetchJson<any>(`${API_BASE}/calendar/propose-slots`, { method: "POST" }),
  scheduleMeeting: (data: any) => 
    fetchJson<any>(`${API_BASE}/calendar/schedule`, { method: "POST", body: JSON.stringify(data) }),

  // Security & Audit
  getSecurityStatus: () => fetchJson<any>(`${API_BASE}/audit/status`),
  toggleKillSwitch: (active: boolean) => 
    fetchJson<any>(`${API_BASE}/audit/kill-switch`, { method: "POST", body: JSON.stringify({ active }) }),

  // Live Platforms & Autonomous Auto-Apply
  getPlatforms: () => fetchJson<any[]>(`${API_BASE}/platforms`),
  connectPlatform: (data: any) => 
    fetchJson<any>(`${API_BASE}/platforms/connect`, { method: "POST", body: JSON.stringify(data) }),
  disconnectPlatform: (platformId: string) => 
    fetchJson<any>(`${API_BASE}/platforms/disconnect?platformId=${encodeURIComponent(platformId)}`, { method: "POST" }),
  addCustomPlatform: (data: any) => 
    fetchJson<any>(`${API_BASE}/platforms/custom`, { method: "POST", body: JSON.stringify(data) }),
  getAutoApplySettings: () => fetchJson<any>(`${API_BASE}/platforms/auto-apply/settings`),
  updateAutoApplySettings: (data: any) => 
    fetchJson<any>(`${API_BASE}/platforms/auto-apply/settings`, { method: "PUT", body: JSON.stringify(data) }),
  runAutoApply: (platformId?: string) => 
    fetchJson<any>(`${API_BASE}/platforms/auto-apply/run`, { method: "POST", body: JSON.stringify({ platformId, forceRun: true }) }),
  getAutoApplyLogs: () => fetchJson<any[]>(`${API_BASE}/platforms/auto-apply/logs`),
};
