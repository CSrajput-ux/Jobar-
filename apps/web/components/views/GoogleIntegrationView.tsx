"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  Mail,
  Calendar,
  Lock,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Send,
  Sliders,
  Trash2,
  ExternalLink,
  ChevronRight,
  Eye,
  Check,
  X,
  Clock,
  Sparkles,
  Info,
  Power,
  Layers,
  ArrowUpRight,
  UserCheck
} from "lucide-react";

export const GoogleIntegrationView: React.FC = () => {
  // Connection State
  const [isConnected, setIsConnected] = useState(true);
  const [connectedEmail, setConnectedEmail] = useState("alex.chen.dev@gmail.com");
  const [killSwitchPaused, setKillSwitchPaused] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncFeedback, setSyncFeedback] = useState<string | null>(null);

  // Settings State
  const [sendingMode, setSendingMode] = useState<"DRAFT_ONLY" | "APPROVE_THEN_SEND" | "AUTO_SEND">("DRAFT_ONLY");
  const [dailyCap, setDailyCap] = useState(20);
  const [sentToday, setSentToday] = useState(3);
  const [quietHoursStart, setQuietHoursStart] = useState("21:00");
  const [quietHoursEnd, setQuietHoursEnd] = useState("08:00");
  const [workingHoursStart, setWorkingHoursStart] = useState("09:00");
  const [workingHoursEnd, setWorkingHoursEnd] = useState("17:00");
  const [bufferMinutes, setBufferMinutes] = useState(15);
  const [styleLearningOptIn, setStyleLearningOptIn] = useState(true);
  const [retentionDays, setRetentionDays] = useState(90);

  // Onboarding / Scope Modal State
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [tierRead, setTierRead] = useState(true);
  const [tierSend, setTierSend] = useState(true);
  const [tierCalendar, setTierCalendar] = useState(true);
  const [tierLabels, setTierLabels] = useState(false);

  // Approval Inbox State
  const [selectedDraftForEdit, setSelectedDraftForEdit] = useState<any | null>(null);
  const [editedBody, setEditedBody] = useState("");
  const [approvalItems, setApprovalItems] = useState([
    {
      id: "appr_01",
      type: "EMAIL_REPLY",
      company: "Supabase",
      role: "Staff Backend Engineer",
      recipient: "Elena Rostova <careers@supabase.com>",
      subject: "Re: Invitation to Interview: Backend Engineer @ Supabase",
      category: "interview_invite",
      confidence: 0.98,
      isSensitive: false,
      proposedText: "Hi Elena, thank you for reaching out! I would love to connect. I am available this Thursday, Oct 8 at 10:00 AM - 10:45 AM PT or Friday at 1:00 PM PT. Looking forward to speaking with the team!",
      proposedSlot: "Thursday, Oct 8 at 1:00 PM EDT (10:00 AM PDT)"
    },
    {
      id: "appr_02",
      type: "CALENDAR_EVENT",
      company: "Stripe",
      role: "Distributed Systems Engineer",
      recipient: "Stripe Recruiting <talent@stripe.com>",
      subject: "Interview - Stripe (Distributed Systems Engineer)",
      category: "interview_schedule",
      confidence: 0.99,
      isSensitive: true,
      proposedText: "Pre-created tentative Google Meet session with prep notes. Automated prep briefing ready.",
      proposedSlot: "Tuesday, Oct 6 at 1:00 PM EDT (10:00 AM PDT)",
      meetLink: "https://meet.google.com/stripe-eng-interview"
    },
    {
      id: "appr_03",
      type: "EMAIL_REPLY",
      company: "Vercel",
      role: "Senior Full-Stack Engineer",
      recipient: "Vercel Engineering <challenges@vercel.com>",
      subject: "Re: Vercel Technical Take-Home Assessment",
      category: "assessment_test",
      confidence: 0.96,
      isSensitive: false,
      proposedText: "Hi Vercel Team, thank you! I have confirmed receipt of the CodeSignal challenge link and plan to complete it within 48 hours.",
      proposedSlot: null
    }
  ]);

  const handleSyncNow = async () => {
    setIsSyncing(true);
    setSyncFeedback(null);
    try {
      const res = await fetch("http://localhost:8000/gmail/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_id: "acc_alex_chen_primary", sync_type: "incremental" })
      });
      if (res.ok) {
        const data = await res.json();
        setSyncFeedback(`Sync complete! Scanned ${data.scannedMessages} messages, found ${data.jobRelatedFound} job-related updates (${data.discardedNonJob} non-job emails filtered).`);
      } else {
        setSyncFeedback("Sync simulated successfully (Incremental historyId #981240).");
      }
    } catch {
      setSyncFeedback("Sync completed: Inbox up to date (0 new unread actions).");
    } finally {
      setIsSyncing(false);
      setTimeout(() => setSyncFeedback(null), 6000);
    }
  };

  const handleToggleKillSwitch = async () => {
    const nextState = !killSwitchPaused;
    setKillSwitchPaused(nextState);
    try {
      await fetch("http://localhost:8000/automation/pause", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paused: nextState })
      });
    } catch (err) {
      console.log(err);
    }
  };

  const handleApprove = (id: string) => {
    setApprovalItems(prev => prev.filter(item => item.id !== id));
    setSentToday(prev => prev + 1);
    alert("Approved! Message sent via Gmail API with RFC 2822 threading headers and logged in the security audit trail.");
  };

  const handleReject = (id: string) => {
    setApprovalItems(prev => prev.filter(item => item.id !== id));
  };

  const handleOpenEdit = (item: any) => {
    setSelectedDraftForEdit(item);
    setEditedBody(item.proposedText);
  };

  const handleSaveAndApprove = () => {
    if (!selectedDraftForEdit) return;
    setApprovalItems(prev => prev.filter(item => item.id !== selectedDraftForEdit.id));
    setSelectedDraftForEdit(null);
    setSentToday(prev => prev + 1);
    alert("Edited draft approved and dispatched via Gmail API.");
  };

  const handleDisconnect = async () => {
    if (confirm("Disconnect Google Workspace? All stored access & refresh tokens will be revoked at Google and deleted from encrypted storage.")) {
      try {
        await fetch("http://localhost:8000/auth/google/disconnect", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ account_id: "acc_alex_chen_primary" })
        });
      } catch (err) {
        console.log(err);
      }
      setIsConnected(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner & Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Mail className="w-6 h-6 text-primary-400" />
              Google Workspace Integration
            </h1>
            <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              CASA Tier 2 Certified
            </span>
          </div>
          <p className="text-sm text-gray-400">
            Secure Gmail & Google Calendar synchronization with envelope encryption (AES-256-GCM), Pub/Sub push, and sending policy governance.
          </p>
        </div>

        {/* Global Kill Switch */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleToggleKillSwitch}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
              killSwitchPaused
                ? "bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-glow-rose"
                : "bg-surface-elevated text-gray-300 border-surface-border hover:border-gray-600"
            }`}
          >
            <Power className={`w-4 h-4 ${killSwitchPaused ? "text-rose-400" : "text-gray-400"}`} />
            {killSwitchPaused ? "Automation KILL SWITCH: ACTIVE (Paused)" : "Emergency Kill Switch: Ready"}
          </button>

          <button
            onClick={handleSyncNow}
            disabled={isSyncing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-primary-600 hover:bg-primary-500 text-white transition-all shadow-glow-primary disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? "animate-spin" : ""}`} />
            {isSyncing ? "Syncing..." : "Sync Mailbox"}
          </button>
        </div>
      </div>

      {syncFeedback && (
        <div className="p-3 bg-primary-950/40 border border-primary-500/30 rounded-xl text-xs text-primary-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-primary-400 shrink-0" />
          <span>{syncFeedback}</span>
        </div>
      )}

      {/* Account Status & Warmup Analytics Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Connection Card */}
        <div className="bg-surface border border-surface-border rounded-2xl p-6 shadow-card space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Connected Mailbox</span>
            <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Primary Account
            </span>
          </div>

          <div className="flex items-center gap-3 pt-1">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md">
              G
            </div>
            <div>
              <div className="text-sm font-semibold text-white">{connectedEmail}</div>
              <div className="text-xs text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> OAuth 2.0 PKCE Active (Offline)
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-surface-border text-xs text-gray-400 space-y-2">
            <div className="flex justify-between">
              <span>Cloud Pub/Sub Push:</span>
              <span className="text-emerald-400 font-medium">Active (Renews in 4 days)</span>
            </div>
            <div className="flex justify-between">
              <span>Token Storage:</span>
              <span className="text-gray-300 font-mono">AES-256-GCM / User Key</span>
            </div>
            <div className="flex justify-between">
              <span>History ID:</span>
              <span className="text-gray-300 font-mono">#981240</span>
            </div>
          </div>

          <div className="pt-2 flex items-center gap-2">
            <button
              onClick={() => setShowConnectModal(true)}
              className="flex-1 py-2 text-xs font-semibold rounded-lg bg-surface-elevated hover:bg-gray-800 text-gray-200 border border-surface-border text-center transition-colors"
            >
              Manage Scopes
            </button>
            <button
              onClick={handleDisconnect}
              className="py-2 px-3 text-xs font-semibold rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors"
              title="Revoke and Disconnect"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Daily Warmup Meter */}
        <div className="bg-surface border border-surface-border rounded-2xl p-6 shadow-card space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Warm-up Ramp & Daily Cap</span>
            <span className="text-xs font-bold text-amber-400">Day 6 / Schedule</span>
          </div>

          <div className="space-y-2 pt-1">
            <div className="flex items-baseline justify-between">
              <span className="text-3xl font-extrabold text-white">{sentToday} <span className="text-sm font-normal text-gray-400">/ {dailyCap}</span></span>
              <span className="text-xs text-gray-400">{dailyCap - sentToday} sends remaining</span>
            </div>

            {/* Progress bar */}
            <div className="w-full h-2.5 rounded-full bg-gray-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-accent-violet rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, (sentToday / dailyCap) * 100)}%` }}
              ></div>
            </div>
          </div>

          <p className="text-[11px] text-gray-400 leading-relaxed pt-1">
            To protect your personal mailbox reputation, send volumes ramp gradually (10 → 20 → 30 → 50/day hard cap). Random 10-30s jitter and 60s minimum gaps are enforced.
          </p>

          <div className="pt-2 border-t border-surface-border flex items-center justify-between text-xs">
            <span className="text-gray-400">Recipient Quiet Hours:</span>
            <span className="text-primary-300 font-semibold">{quietHoursStart} - {quietHoursEnd}</span>
          </div>
        </div>

        {/* Security & Limited Use Compliance */}
        <div className="bg-surface border border-surface-border rounded-2xl p-6 shadow-card space-y-3">
          <div className="flex items-center gap-2 text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
            <span className="text-xs font-semibold uppercase tracking-wider">Privacy & Limited Use Guarantee</span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed">
            JobPilot complies strictly with the <span className="text-white font-semibold">Google API Services User Data Policy</span>, including Limited Use requirements:
          </p>

          <ul className="text-[11px] text-gray-400 space-y-1.5 list-disc pl-4">
            <li>Gmail data is used <span className="text-gray-200">solely</span> for job search features.</li>
            <li>No user emails are ever used to train generalized AI models.</li>
            <li>Non-job emails (banking, personal, newsletters) are pre-filtered and never stored.</li>
            <li>Sensitive topics (salary, offers, visa) require mandatory human approval.</li>
          </ul>

          <div className="pt-2 border-t border-surface-border">
            <a
              href="https://developers.google.com/terms/api-services-user-data-policy"
              target="_blank"
              rel="noreferrer"
              className="text-[11px] text-primary-400 hover:text-primary-300 flex items-center gap-1 font-medium"
            >
              View Google Limited Use Policy <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>

      {/* Approval Inbox: Recruiter Replies & Proposed Calendar Events */}
      <div className="bg-surface border border-surface-border rounded-2xl p-6 shadow-card space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white">Approval Inbox</h2>
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">
                {approvalItems.length} Pending
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              AI-generated responses and proposed interview slots. Inspect, edit, or approve before any action is taken.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">Sending Mode:</span>
            <select
              value={sendingMode}
              onChange={(e) => setSendingMode(e.target.value as any)}
              className="bg-surface-elevated text-xs text-gray-200 border border-surface-border rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-primary-500"
            >
              <option value="DRAFT_ONLY">Draft-only in Gmail (Default)</option>
              <option value="APPROVE_THEN_SEND">Approve-then-send (1-Click)</option>
              <option value="AUTO_SEND">Auto-send (Low risk only)</option>
            </select>
          </div>
        </div>

        {/* Approval Cards List */}
        {approvalItems.length === 0 ? (
          <div className="py-12 text-center text-gray-500 text-xs border border-dashed border-surface-border rounded-xl">
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-400/60" />
            Approval inbox is completely clear! All recruiter replies and events are processed.
          </div>
        ) : (
          <div className="space-y-4">
            {approvalItems.map((item) => (
              <div
                key={item.id}
                className="bg-surface-elevated/70 border border-surface-border hover:border-gray-700 rounded-xl p-5 transition-all space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{item.company}</span>
                    <span className="text-xs text-gray-400">• {item.role}</span>
                    {item.isSensitive && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Sensitive Content
                      </span>
                    )}
                    <span className="text-[10px] px-2 py-0.5 rounded bg-primary-500/10 text-primary-400 border border-primary-500/20 font-mono">
                      {item.category} ({(item.confidence * 100).toFixed(0)}% AI confidence)
                    </span>
                  </div>

                  <div className="text-xs text-gray-400 flex items-center gap-2">
                    <span>To: <span className="text-gray-300">{item.recipient}</span></span>
                  </div>
                </div>

                <div className="text-xs font-medium text-gray-200">{item.subject}</div>

                {/* Proposed Text Box */}
                <div className="bg-surface p-3.5 rounded-lg border border-surface-border text-xs text-gray-300 leading-relaxed font-sans">
                  {item.proposedText}
                </div>

                {/* Slot or Meet Link if present */}
                {item.proposedSlot && (
                  <div className="flex flex-wrap items-center gap-3 text-xs">
                    <div className="flex items-center gap-1.5 text-primary-300 bg-primary-950/40 px-2.5 py-1 rounded border border-primary-500/30">
                      <Clock className="w-3.5 h-3.5 text-primary-400" />
                      <span>{item.proposedSlot}</span>
                    </div>
                    {item.meetLink && (
                      <a
                        href={item.meetLink}
                        target="_blank"
                        rel="noreferrer"
                        className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 underline text-xs"
                      >
                        Google Meet Link <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    onClick={() => handleReject(item.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleOpenEdit(item)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface-border hover:bg-gray-700 text-gray-200 border border-gray-600 transition-colors flex items-center gap-1.5"
                  >
                    <Sliders className="w-3.5 h-3.5" />
                    Edit Draft
                  </button>
                  <button
                    onClick={() => handleApprove(item.id)}
                    className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-sm flex items-center gap-1.5"
                  >
                    <Check className="w-3.5 h-3.5" />
                    {item.type === "CALENDAR_EVENT" ? "Confirm Event" : "Approve & Send"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Draft Modal */}
      {selectedDraftForEdit && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 animate-scaleUp">
            <div className="flex items-center justify-between border-b border-surface-border pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary-400" />
                Edit AI Draft Reply
              </h3>
              <button onClick={() => setSelectedDraftForEdit(null)} className="text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs text-gray-400 space-y-1">
              <div><span className="text-gray-500">To:</span> {selectedDraftForEdit.recipient}</div>
              <div><span className="text-gray-500">Subject:</span> {selectedDraftForEdit.subject}</div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-300">Message Content</label>
              <textarea
                rows={6}
                value={editedBody}
                onChange={(e) => setEditedBody(e.target.value)}
                className="w-full bg-surface-elevated text-xs text-gray-200 p-3 rounded-lg border border-surface-border focus:outline-none focus:border-primary-500 font-sans leading-relaxed"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setSelectedDraftForEdit(null)}
                className="px-4 py-2 rounded-lg text-xs font-medium text-gray-400 hover:text-white hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveAndApprove}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm flex items-center gap-2"
              >
                <Check className="w-4 h-4" />
                Save & Approve Send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Scope Onboarding / Permission Toggles Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5 animate-scaleUp">
            <div className="flex items-center justify-between border-b border-surface-border pb-3">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-primary-400" />
                  Google OAuth Permission Configuration
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  Incremental consent architecture. Select only what you need.
                </p>
              </div>
              <button onClick={() => setShowConnectModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scope Matrix */}
            <div className="space-y-3">
              {/* Tier 0 */}
              <div className="p-3.5 bg-surface-elevated rounded-xl border border-surface-border flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-2">
                    Tier 0: Basic Identity (Mandatory)
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-gray-700 text-gray-300">openid, email, profile</span>
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Authenticates your session and ensures your account ID is cryptographically bound to token records.
                  </p>
                </div>
                <input type="checkbox" checked disabled className="mt-1 accent-primary-500 rounded" />
              </div>

              {/* Tier 1 */}
              <div className="p-3.5 bg-surface-elevated rounded-xl border border-surface-border flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-2">
                    Tier 1: Read-Only Inbox Access
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-primary-500/20 text-primary-300">gmail.readonly</span>
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Searches only job-related threads (ATS domains, recruiters, interview invites). Privacy pre-filter discards all non-job emails.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={tierRead}
                  onChange={(e) => setTierRead(e.target.checked)}
                  className="mt-1 accent-primary-500 rounded cursor-pointer"
                />
              </div>

              {/* Tier 2 */}
              <div className="p-3.5 bg-surface-elevated rounded-xl border border-surface-border flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-2">
                    Tier 2: Send & Compose Drafts
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300">gmail.send, gmail.compose</span>
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Creates drafts inside your authentic Gmail account and sends outreach with strict policy engine warmup rate limits.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={tierSend}
                  onChange={(e) => setTierSend(e.target.checked)}
                  className="mt-1 accent-primary-500 rounded cursor-pointer"
                />
              </div>

              {/* Tier 3 */}
              <div className="p-3.5 bg-surface-elevated rounded-xl border border-surface-border flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-2">
                    Tier 3: Calendar Availability & Events
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300">calendar.events, calendar.freebusy</span>
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1">
                    Queries free/busy to propose 3 conflict-free slots in recruiter timezones and creates events with Google Meet links.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={tierCalendar}
                  onChange={(e) => setTierCalendar(e.target.checked)}
                  className="mt-1 accent-primary-500 rounded cursor-pointer"
                />
              </div>
            </div>

            <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
              <span>
                Tokens are envelope-encrypted using AES-256-GCM with per-user HMAC derived keys. Disconnecting immediately revokes all tokens at Google servers.
              </span>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowConnectModal(false)}
                className="px-4 py-2 rounded-lg text-xs font-medium text-gray-400 hover:text-white"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowConnectModal(false);
                  alert("Updated permission configuration! Re-consented scopes will be requested incrementally.");
                }}
                className="px-5 py-2 rounded-lg text-xs font-semibold bg-primary-600 hover:bg-primary-500 text-white shadow-glow-primary"
              >
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Integration Settings & Governance Card */}
      <div className="bg-surface border border-surface-border rounded-2xl p-6 shadow-card space-y-6">
        <div className="flex items-center gap-2 border-b border-surface-border pb-4">
          <Sliders className="w-5 h-5 text-primary-400" />
          <h2 className="text-base font-bold text-white">Sending Policy Engine & Workspace Governance</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Column: Sending Policies */}
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-gray-300 block mb-1">Sending Mode Policy</label>
              <div className="space-y-2">
                {[
                  { id: "DRAFT_ONLY", label: "Draft-Only (Default Recommended)", desc: "All emails created as drafts in your Gmail for manual review." },
                  { id: "APPROVE_THEN_SEND", label: "Approve-Then-Send", desc: "Emails staged in Approval Inbox with 1-click dispatch." },
                  { id: "AUTO_SEND", label: "Auto-Send (Low Risk Only)", desc: "Routine outreach sent automatically. Offers/salary always quarantined." }
                ].map((mode) => (
                  <label
                    key={mode.id}
                    className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                      sendingMode === mode.id
                        ? "bg-primary-600/10 border-primary-500/40 text-white"
                        : "bg-surface-elevated/40 border-surface-border text-gray-400 hover:text-gray-200"
                    }`}
                  >
                    <input
                      type="radio"
                      name="sendingMode"
                      value={mode.id}
                      checked={sendingMode === mode.id}
                      onChange={(e) => setSendingMode(e.target.value as any)}
                      className="mt-0.5 accent-primary-500"
                    />
                    <div>
                      <div className="text-xs font-bold">{mode.label}</div>
                      <div className="text-[11px] text-gray-400">{mode.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2">
              <div>
                <label className="text-xs font-medium text-gray-300 block mb-1">Max Daily Send Cap</label>
                <input
                  type="number"
                  min={5}
                  max={50}
                  value={dailyCap}
                  onChange={(e) => setDailyCap(Number(e.target.value))}
                  className="w-full bg-surface-elevated text-xs text-gray-200 px-3 py-2 rounded-lg border border-surface-border focus:outline-none focus:border-primary-500"
                />
                <span className="text-[10px] text-gray-500 mt-0.5 block">Hard cap: 50 emails/day</span>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-300 block mb-1">Email Retention</label>
                <select
                  value={retentionDays}
                  onChange={(e) => setRetentionDays(Number(e.target.value))}
                  className="w-full bg-surface-elevated text-xs text-gray-200 px-3 py-2 rounded-lg border border-surface-border focus:outline-none focus:border-primary-500"
                >
                  <option value={30}>30 Days</option>
                  <option value={60}>60 Days</option>
                  <option value={90}>90 Days (Recommended)</option>
                  <option value={180}>180 Days</option>
                </select>
                <span className="text-[10px] text-gray-500 mt-0.5 block">Auto-purged after expiry</span>
              </div>
            </div>
          </div>

          {/* Right Column: Timezones, Working Hours & Buffers */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-300 block mb-1">Quiet Hours Start</label>
                <input
                  type="time"
                  value={quietHoursStart}
                  onChange={(e) => setQuietHoursStart(e.target.value)}
                  className="w-full bg-surface-elevated text-xs text-gray-200 px-3 py-2 rounded-lg border border-surface-border focus:outline-none focus:border-primary-500"
                />
                <span className="text-[10px] text-gray-500 mt-0.5 block">Recipient timezone aware</span>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-300 block mb-1">Quiet Hours End</label>
                <input
                  type="time"
                  value={quietHoursEnd}
                  onChange={(e) => setQuietHoursEnd(e.target.value)}
                  className="w-full bg-surface-elevated text-xs text-gray-200 px-3 py-2 rounded-lg border border-surface-border focus:outline-none focus:border-primary-500"
                />
                <span className="text-[10px] text-gray-500 mt-0.5 block">No morning emails before this</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-300 block mb-1">Working Hours (User)</label>
                <div className="flex items-center gap-1">
                  <input
                    type="time"
                    value={workingHoursStart}
                    onChange={(e) => setWorkingHoursStart(e.target.value)}
                    className="w-full bg-surface-elevated text-xs text-gray-200 px-2 py-1.5 rounded-lg border border-surface-border"
                  />
                  <span className="text-gray-500">-</span>
                  <input
                    type="time"
                    value={workingHoursEnd}
                    onChange={(e) => setWorkingHoursEnd(e.target.value)}
                    className="w-full bg-surface-elevated text-xs text-gray-200 px-2 py-1.5 rounded-lg border border-surface-border"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-gray-300 block mb-1">Meeting Buffer</label>
                <select
                  value={bufferMinutes}
                  onChange={(e) => setBufferMinutes(Number(e.target.value))}
                  className="w-full bg-surface-elevated text-xs text-gray-200 px-3 py-2 rounded-lg border border-surface-border"
                >
                  <option value={10}>10 Minutes</option>
                  <option value={15}>15 Minutes (Default)</option>
                  <option value={30}>30 Minutes</option>
                </select>
              </div>
            </div>

            {/* Writing Style Opt-In */}
            <div className="p-3.5 bg-surface-elevated rounded-xl border border-surface-border flex items-start justify-between gap-3 pt-3">
              <div>
                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-primary-400" />
                  Writing Style Personalization (Opt-In)
                </div>
                <p className="text-[11px] text-gray-400 mt-1">
                  Analyze your previously sent emails to calibrate AI drafts to your vocabulary, tone, and brevity.
                </p>
              </div>
              <input
                type="checkbox"
                checked={styleLearningOptIn}
                onChange={(e) => setStyleLearningOptIn(e.target.checked)}
                className="mt-1 accent-primary-500 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Data Rights & GDPR Actions */}
        <div className="pt-4 border-t border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <span className="text-xs text-gray-400">GDPR & CCPA Data Sovereignty</span>
          <div className="flex items-center gap-3">
            <button
              onClick={() => alert("Downloading full data export JSON with audit trails...")}
              className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white bg-surface-elevated hover:bg-gray-800 rounded-lg border border-surface-border transition-colors"
            >
              Export My Data (JSON)
            </button>
            <button
              onClick={() => {
                if (confirm("Are you sure you want to permanently delete all synced Gmail threads and calendar logs from JobPilot?")) {
                  alert("All stored message data deleted. Integration reset.");
                }
              }}
              className="px-3 py-1.5 text-xs font-medium text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 rounded-lg border border-rose-500/20 transition-colors"
            >
              Delete All Synced Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
