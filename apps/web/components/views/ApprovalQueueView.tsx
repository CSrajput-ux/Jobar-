"use client";

import React, { useState } from "react";
import { 
  CheckSquare, 
  CheckCircle2, 
  XCircle, 
  Edit3, 
  Sparkles, 
  ShieldCheck, 
  HelpCircle,
  Building,
  ArrowRight,
  ExternalLink
} from "lucide-react";

interface ApprovalQueueViewProps {
  onApproveApplication: (appId: string) => void;
  onOpenTailoring: (job: any) => void;
}

export const ApprovalQueueView: React.FC<ApprovalQueueViewProps> = ({
  onApproveApplication,
  onOpenTailoring
}) => {
  const [queueItems, setQueueItems] = useState([
    {
      id: "10000000-0000-0000-0000-000000000001",
      companyName: "Vercel",
      title: "Senior Full-Stack Engineer, AI Platforms",
      location: "Remote (United States)",
      atsType: "greenhouse",
      salary: "$170,000 - $210,000 + Equity",
      matchScore: 96,
      tailoredSummary: "Optimized for Next.js App Router, streaming LLM endpoints, and high-throughput Python backends.",
      qaFields: [
        { label: "Work Authorization", value: "Authorized to work in US without sponsorship", confidence: 1.0 },
        { label: "Notice Period", value: "2 weeks (14 days)", confidence: 1.0 },
        { label: "Expected Salary", value: "$185,000 USD", confidence: 0.95 },
        { label: "Why Vercel?", value: "Passionate about empowering developers with seamless frontend and AI orchestration platforms.", confidence: 0.92 }
      ],
      bulletHighlights: [
        "Architected event-driven microservices processing 45M daily events with 99.99% availability using FastAPI and Next.js.",
        "Engineered production AI vector search infrastructure using pgvector, cutting latency by 90%."
      ]
    }
  ]);

  const handleApprove = (id: string) => {
    onApproveApplication(id);
    setQueueItems(prev => prev.filter(item => item.id !== id));
  };

  const handleReject = (id: string) => {
    setQueueItems(prev => prev.filter(item => item.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-amber-400" />
            Candidate Approval Queue
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Human-in-the-loop review. Inspect pre-filled ATS answers and tailored bullets before Playwright executes submission.
          </p>
        </div>

        {queueItems.length > 0 && (
          <button
            onClick={() => handleApprove(queueItems[0].id)}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-glow-emerald flex items-center gap-2 transition-all"
          >
            <CheckCircle2 className="w-4 h-4" />
            Approve All ({queueItems.length})
          </button>
        )}
      </div>

      {queueItems.length === 0 ? (
        <div className="p-12 text-center rounded-2xl glass-panel border border-surface-border space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 mx-auto flex items-center justify-center">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white">Queue is clear!</h3>
          <p className="text-xs text-gray-400 max-w-md mx-auto">
            All pending applications have been approved and submitted via Playwright. New discovered matches will appear here automatically.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {queueItems.map((item) => (
            <div
              key={item.id}
              className="p-6 rounded-2xl glass-card border border-surface-border space-y-5"
            >
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-gray-300">{item.companyName}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded uppercase font-semibold bg-surface-elevated text-gray-400 border border-surface-border">
                      {item.atsType}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {item.matchScore}% Match
                    </span>
                  </div>
                  <h2 className="text-base font-bold text-white">{item.title}</h2>
                  <p className="text-xs text-gray-400 mt-0.5">{item.location} • {item.salary}</p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleReject(item.id)}
                    className="p-2 text-gray-400 hover:text-rose-400 rounded-lg hover:bg-surface-elevated transition-colors"
                    title="Reject / Remove from queue"
                  >
                    <XCircle className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleApprove(item.id)}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-glow-emerald flex items-center gap-1.5 transition-all"
                  >
                    <CheckCircle2 className="w-4 h-4" /> 1-Click Approve & Submit
                  </button>
                </div>
              </div>

              {/* Proposed Tailored Highlights */}
              <div className="bg-surface/80 p-4 rounded-xl border border-surface-border space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-gray-200 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-primary-400" /> Tailored Resume Highlights (Zero-Fabrication Guardrail)
                  </span>
                  <button
                    onClick={() => onOpenTailoring({ companyName: item.companyName, title: item.title })}
                    className="text-primary-400 hover:text-primary-300 font-semibold flex items-center gap-1 text-[11px]"
                  >
                    <Edit3 className="w-3 h-3" /> Edit in Resume Studio
                  </button>
                </div>
                <ul className="space-y-1.5 text-xs text-gray-300">
                  {item.bulletHighlights.map((b, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-primary-400 mt-1">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Form Answers & AI Confidence */}
              <div>
                <h4 className="text-xs font-bold text-gray-300 mb-2 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  ATS Form Questions & Answers
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {item.qaFields.map((field, i) => (
                    <div key={i} className="p-3 rounded-lg bg-surface-elevated border border-surface-border/60">
                      <div className="flex items-center justify-between text-[11px] text-gray-400 mb-1">
                        <span>{field.label}</span>
                        <span className="text-[10px] text-emerald-400 font-semibold">
                          {Math.round(field.confidence * 100)}% Confidence
                        </span>
                      </div>
                      <div className="font-medium text-gray-200">{field.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
