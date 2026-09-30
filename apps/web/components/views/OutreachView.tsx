"use client";

import React, { useState } from "react";
import { 
  Send, 
  Sparkles, 
  UserCheck, 
  ExternalLink, 
  CheckCircle2, 
  Clock, 
  Mail, 
  Shield, 
  Sliders,
  Check
} from "lucide-react";

export const OutreachView: React.FC = () => {
  const [selectedContact, setSelectedContact] = useState<any>({
    id: "20000000-0000-0000-0000-000000000001",
    companyName: "Vercel",
    fullName: "Sarah Jenkins",
    roleTitle: "Senior Technical Recruiter (Engineering)",
    email: "sarah.j@vercel.com",
    linkedinUrl: "https://linkedin.com/in/sarah-jenkins-tech",
    isVerified: true
  });

  const [selectedTone, setSelectedTone] = useState<"confident_professional" | "casual_warm" | "metrics_driven">("confident_professional");
  const [emailSubject, setEmailSubject] = useState("Building AI web applications @ Vercel — Alex Chen");
  const [emailBody, setEmailBody] = useState(
    "Hi Sarah,\n\nI noticed Vercel is scaling the AI Platforms team. Over the past 4 years, I have architected high-performance Next.js systems and distributed LLM pipelines, including an open-source queue gateway that handles 45M daily events.\n\nI submitted an application for the Senior Full-Stack role and would welcome 10 minutes to connect if my background aligns with your roadmap.\n\nBest regards,\nAlex Chen | https://github.com/alexchen\n\n---\nReply 'unsubscribe' to opt out of future messages."
  );

  const [isSending, setIsSending] = useState(false);
  const [sentSuccess, setSentSuccess] = useState(false);

  const contacts = [
    {
      id: "20000000-0000-0000-0000-000000000001",
      companyName: "Vercel",
      fullName: "Sarah Jenkins",
      roleTitle: "Senior Technical Recruiter (Engineering)",
      email: "sarah.j@vercel.com",
      linkedinUrl: "https://linkedin.com/in/sarah-jenkins-tech",
      isVerified: true
    },
    {
      id: "20000000-0000-0000-0000-000000000002",
      companyName: "Linear",
      fullName: "Marcus Vance",
      roleTitle: "Head of Engineering Talent",
      email: "marcus@linear.app",
      linkedinUrl: "https://linkedin.com/in/marcus-vance-linear",
      isVerified: true
    },
    {
      id: "20000000-0000-0000-0000-000000000003",
      companyName: "Supabase",
      fullName: "Elena Rostova",
      roleTitle: "Lead Tech Recruiter",
      email: "elena.r@supabase.com",
      linkedinUrl: "https://linkedin.com/in/elena-rostova",
      isVerified: true
    }
  ];

  const handleToneChange = (tone: "confident_professional" | "casual_warm" | "metrics_driven") => {
    setSelectedTone(tone);
    if (tone === "casual_warm") {
      setEmailSubject(`Senior Full-Stack role @ ${selectedContact.companyName} — quick intro`);
      setEmailBody(
        `Hi ${selectedContact.fullName.split(" ")[0]},\n\nLoved seeing ${selectedContact.companyName}'s developer platform velocity. Over the last few years, I've built scalable cloud services handling 40M+ daily events and fast web frontends.\n\nI recently submitted my application, but wanted to reach out directly in case a quick chat makes sense. Would love to share how my background fits your team's goals.\n\nBest,\nAlex Chen\n\n---\nReply 'unsubscribe' to opt out.`
      );
    } else if (tone === "metrics_driven") {
      setEmailSubject(`Senior Full-Stack @ ${selectedContact.companyName} — 90% latency reduction & 45M events/day`);
      setEmailBody(
        `Hi ${selectedContact.fullName},\n\nI recently applied for the Senior Full-Stack position at ${selectedContact.companyName}. My background centers on high-scale distributed systems: cutting vector lookup times by 90% and maintaining 99.99% uptime across 45M daily operations.\n\nI would appreciate 10 minutes to discuss how these engineering patterns can accelerate your team's roadmap.\n\nRegards,\nAlex Chen\n\n---\nReply 'unsubscribe' to opt out.`
      );
    } else {
      setEmailSubject(`Building AI web applications @ ${selectedContact.companyName} — Alex Chen`);
      setEmailBody(
        `Hi ${selectedContact.fullName},\n\nI noticed ${selectedContact.companyName} is scaling the engineering team for AI Platforms. Over the past 4 years, I have architected high-performance Next.js systems and distributed LLM pipelines, including an open-source queue gateway that handles 45M daily events.\n\nI submitted an application for the Senior Full-Stack role and would welcome 10 minutes to connect if my background aligns with your roadmap.\n\nBest regards,\nAlex Chen | https://github.com/alexchen\n\n---\nReply 'unsubscribe' to opt out.`
      );
    }
  };

  const handleSendViaGmail = () => {
    setIsSending(true);
    setTimeout(() => {
      setIsSending(false);
      setSentSuccess(true);
      setTimeout(() => setSentSuccess(false), 3000);
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Send className="w-5 h-5 text-primary-400" />
            Recruiter Cold Outreach & Sequences
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Sent exclusively through your connected Gmail mailbox with automatic warmup limits and CAN-SPAM compliance.
          </p>
        </div>

        {/* Warmup Rate Indicator */}
        <div className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-surface-elevated border border-surface-border text-xs">
          <Mail className="w-4 h-4 text-emerald-400" />
          <span className="text-gray-300">Warmup Day 1:</span>
          <span className="font-bold text-emerald-400">0 / 10 sent today</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recruiter Contacts List (1 col) */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Verified Recruiters (Hunter.io / Apollo)
          </h3>

          <div className="space-y-2">
            {contacts.map((c) => {
              const isSelected = selectedContact.id === c.id;
              return (
                <div
                  key={c.id}
                  onClick={() => {
                    setSelectedContact(c);
                    handleToneChange(selectedTone);
                  }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-primary-950/30 border-primary-500/50 shadow-sm"
                      : "glass-card border-surface-border hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold text-xs text-white">{c.fullName}</span>
                        {c.isVerified && (
                          <span title="Verified email">
                            <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-primary-300">{c.roleTitle}</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">{c.companyName} • {c.email}</div>
                    </div>
                    <a
                      href={c.linkedinUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="p-1 text-gray-400 hover:text-white"
                      title="View LinkedIn"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Composer & Sequence (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-surface-border">
              <div>
                <span className="text-xs text-gray-400">Recipient:</span>
                <span className="text-xs font-bold text-white ml-1.5">
                  {selectedContact.fullName} ({selectedContact.email})
                </span>
              </div>

              {/* Tone Switcher */}
              <div className="flex items-center gap-1.5 bg-surface-elevated p-1 rounded-lg border border-surface-border text-[11px]">
                <button
                  onClick={() => handleToneChange("confident_professional")}
                  className={`px-2.5 py-1 rounded font-medium transition-all ${
                    selectedTone === "confident_professional"
                      ? "bg-primary-600 text-white font-bold"
                      : "text-gray-400 hover:text-gray-200"
                  }`}
                >
                  Professional
                </button>
                <button
                  onClick={() => handleToneChange("casual_warm")}
                  className={`px-2.5 py-1 rounded font-medium transition-all ${
                    selectedTone === "casual_warm"
                      ? "bg-primary-600 text-white font-bold"
                      : "text-gray-400 hover:text-gray-200"
                  }`}
                >
                  Casual Warm
                </button>
                <button
                  onClick={() => handleToneChange("metrics_driven")}
                  className={`px-2.5 py-1 rounded font-medium transition-all ${
                    selectedTone === "metrics_driven"
                      ? "bg-primary-600 text-white font-bold"
                      : "text-gray-400 hover:text-gray-200"
                  }`}
                >
                  Metrics Driven
                </button>
              </div>
            </div>

            {/* Email Subject */}
            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-gray-400">Subject Line</label>
              <input
                type="text"
                value={emailSubject}
                onChange={(e) => setEmailSubject(e.target.value)}
                className="w-full px-3.5 py-2 bg-surface/70 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500"
              />
            </div>

            {/* Email Body */}
            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-gray-400 flex items-center justify-between">
                <span>Personalized Email Body (&lt;120 words)</span>
                <span className="text-[10px] text-emerald-400 font-normal">CAN-SPAM Compliant</span>
              </label>
              <textarea
                rows={8}
                value={emailBody}
                onChange={(e) => setEmailBody(e.target.value)}
                className="w-full p-3.5 bg-surface/70 border border-surface-border rounded-lg text-xs text-white leading-relaxed focus:outline-none focus:border-primary-500 font-sans"
              />
            </div>

            {/* 3-Step Sequence Roadmap */}
            <div className="p-3 bg-surface-elevated/40 rounded-xl border border-surface-border text-xs space-y-2">
              <div className="font-bold text-gray-300 text-[11px] flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-primary-400" /> Automated Sequence Timeline:
              </div>
              <div className="grid grid-cols-3 gap-2 text-[10px] text-gray-400 text-center">
                <div className="p-2 rounded bg-surface border border-surface-border">
                  <div className="font-bold text-primary-300">Step 1: Day 0</div>
                  <div>Introduction (Current)</div>
                </div>
                <div className="p-2 rounded bg-surface border border-surface-border">
                  <div className="font-bold text-gray-300">Step 2: Day 3</div>
                  <div>Gentle Bump / Project Update</div>
                </div>
                <div className="p-2 rounded bg-surface border border-surface-border">
                  <div className="font-bold text-gray-300">Step 3: Day 7</div>
                  <div>Final Nudge (Auto-stops on reply)</div>
                </div>
              </div>
            </div>

            {/* Send Controls */}
            <div className="pt-2 flex items-center justify-between">
              <div className="text-[11px] text-gray-500 flex items-center gap-1">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                Sent via alex.chen.dev@gmail.com
              </div>

              <button
                onClick={handleSendViaGmail}
                disabled={isSending}
                className="px-5 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {sentSuccess ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-300" />
                    <span>Sent via Gmail!</span>
                  </>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>{isSending ? "Sending via Gmail API..." : "Send via Gmail"}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
