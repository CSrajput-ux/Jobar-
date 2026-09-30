"use client";

import React, { useState } from "react";
import { 
  Inbox, 
  Mail, 
  Calendar, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Send, 
  ChevronRight, 
  X,
  Check,
  Building
} from "lucide-react";

export const InboxView: React.FC = () => {
  const [threads, setThreads] = useState([
    {
      id: "50000000-0000-0000-0000-000000000001",
      companyName: "Supabase",
      role: "Backend Engineer, Postgres & Vector Engine",
      sender: "careers@supabase.com",
      subject: "Invitation to Interview: Backend Engineer @ Supabase",
      receivedAt: "3 hours ago",
      classification: "INTERVIEW_INVITE",
      classificationLabel: "Interview Invitation",
      snippet: "Hi Alex, thanks for your application. The engineering team reviewed your background with pgvector and would love to schedule a 30-minute technical intro...",
      fullBody: `Hi Alex,

Thank you for your application for the Backend Engineer, Postgres & Vector Engine role at Supabase.

Our engineering team thoroughly reviewed your background and was especially impressed with your direct experience optimizing pgvector queries and distributed event pipelines.

We would love to schedule a 30-minute introductory conversation to discuss the role and answer any questions you have about Supabase. Please let us know your availability over the next few days.

Best regards,
Elena Rostova
Talent Partner, Supabase`,
      proposedReply: `Hi Elena,

Thank you for reaching out! I would love to connect with the Supabase team.

I am generally available this Thursday and Friday between 10:00 AM - 4:00 PM PT. Please feel free to send through an invite that suits your schedule.

Looking forward to our conversation!

Best regards,
Alex Chen`,
      actionRequired: true,
      autoUpdatedPipeline: "Advanced to 'Interviews' stage in Kanban"
    },
    {
      id: "50000000-0000-0000-0000-000000000002",
      companyName: "Stripe",
      role: "Staff Infrastructure Engineer",
      sender: "talent@stripe.com",
      subject: "Update regarding your application at Stripe",
      receivedAt: "Yesterday",
      classification: "REJECTION",
      classificationLabel: "Rejection",
      snippet: "Thank you for taking the time to speak with our team. While we were impressed by your background, we have decided to move forward with other candidates...",
      fullBody: `Hi Alex,

Thank you for taking the time to consider Stripe. While your experience in distributed infrastructure is impressive, we have decided to move forward with other candidates whose specific domain specialization more closely matches our immediate roadmap.

We wish you the very best in your search and hope to stay in touch for future opportunities.

Warmly,
The Stripe Recruiting Team`,
      proposedReply: null,
      actionRequired: false,
      autoUpdatedPipeline: "Moved to 'Archived' stage"
    }
  ]);

  const [activeThread, setActiveThread] = useState<any>(threads[0]);
  const [replyText, setReplyText] = useState(threads[0]?.proposedReply || "");
  const [isSending, setIsSending] = useState(false);
  const [sentSuccess, setSentSuccess] = useState(false);

  const handleSelectThread = (t: any) => {
    setActiveThread(t);
    setReplyText(t.proposedReply || "");
  };

  const handleSendReply = () => {
    setIsSending(true);
    setTimeout(() => {
      setIsSending(false);
      setSentSuccess(true);
      setTimeout(() => setSentSuccess(false), 2500);
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Inbox className="w-5 h-5 text-primary-400" />
            Inbox Intelligence & Intent Classification
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real-time Gmail Pub/Sub sync. Automatic intent parsing, pipeline stage advancement, and context-aware draft generation.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-elevated border border-surface-border text-xs text-gray-300">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>Gmail Watcher: Connected</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threads List (1 col) */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Candidate Inbound Messages
          </h3>

          <div className="space-y-2">
            {threads.map((t) => {
              const isSelected = activeThread.id === t.id;
              const isInvite = t.classification === "INTERVIEW_INVITE";
              return (
                <div
                  key={t.id}
                  onClick={() => handleSelectThread(t)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-primary-950/30 border-primary-500/50 shadow-sm"
                      : "glass-card border-surface-border hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <span className="text-xs font-bold text-white">{t.companyName}</span>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                        isInvite
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : "bg-zinc-800 text-gray-400 border border-zinc-700"
                      }`}
                    >
                      {t.classificationLabel}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-gray-200 line-clamp-1">
                    {t.subject}
                  </h4>
                  <p className="text-[11px] text-gray-400 line-clamp-2 mt-1">
                    {t.snippet}
                  </p>

                  <div className="flex items-center justify-between text-[10px] text-gray-500 mt-2.5 pt-2 border-t border-surface-border/50">
                    <span>{t.receivedAt}</span>
                    {t.actionRequired && (
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        • Action Required
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Thread Details & Reply Composer (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          {activeThread ? (
            <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-4">
              {/* Header */}
              <div className="pb-4 border-b border-surface-border flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-gray-300">{activeThread.companyName}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold uppercase">
                      {activeThread.classificationLabel}
                    </span>
                  </div>
                  <h2 className="text-base font-bold text-white">{activeThread.subject}</h2>
                  <div className="text-xs text-gray-400 mt-0.5">
                    From: <span className="text-gray-200 font-medium">{activeThread.sender}</span>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[11px] font-semibold text-primary-400 bg-primary-500/10 px-2.5 py-1 rounded-lg border border-primary-500/20">
                    {activeThread.autoUpdatedPipeline}
                  </div>
                </div>
              </div>

              {/* Message Body */}
              <div className="bg-surface/70 p-4 rounded-xl border border-surface-border text-xs text-gray-300 whitespace-pre-line leading-relaxed font-sans">
                {activeThread.fullBody}
              </div>

              {/* Context-aware Reply Composer */}
              {activeThread.actionRequired && (
                <div className="pt-2 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-gray-200 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-primary-400" />
                      AI Context-Aware Draft Reply (GCal Synced)
                    </span>
                    <span className="text-[10px] text-gray-400">Thread-aware reply</span>
                  </div>

                  <textarea
                    rows={5}
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    className="w-full p-3.5 bg-surface/80 border border-surface-border rounded-xl text-xs text-white leading-relaxed focus:outline-none focus:border-primary-500 font-sans"
                  />

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[11px] text-gray-500">
                      Dispatched directly to {activeThread.sender}
                    </span>
                    <button
                      onClick={handleSendReply}
                      disabled={isSending}
                      className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-glow-emerald flex items-center gap-2 transition-all disabled:opacity-50"
                    >
                      {sentSuccess ? (
                        <>
                          <Check className="w-4 h-4 text-emerald-200" />
                          <span>Sent via Gmail!</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>{isSending ? "Sending..." : "Send Reply via Gmail"}</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-64 glass-panel rounded-2xl flex items-center justify-center text-xs text-gray-500">
              Select an email thread to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
