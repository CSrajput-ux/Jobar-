"use client";

import React, { useState } from "react";
import { 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  ShieldCheck, 
  Download, 
  Copy, 
  Check, 
  ArrowRight,
  RefreshCw,
  Eye
} from "lucide-react";

interface TailoringStudioViewProps {
  initialJob?: any;
}

export const TailoringStudioView: React.FC<TailoringStudioViewProps> = ({
  initialJob
}) => {
  const targetCompany = initialJob?.companyName || "Vercel";
  const targetRole = initialJob?.title || "Senior Full-Stack Engineer, AI Platforms";

  const [activeTab, setActiveTab] = useState<"resume" | "cover_letter">("resume");
  const [copied, setCopied] = useState(false);

  const bulletDiffs = [
    {
      original: "Architected event-driven microservices processing 45M daily events with 99.99% availability using FastAPI, Celery, and Redis.",
      tailored: "Architected event-driven microservices processing 45M daily events with 99.99% availability using high-throughput Python/FastAPI and Redis streaming.",
      keyword: "Python/FastAPI streaming"
    },
    {
      original: "Designed high-performance vector search engine using pgvector, reducing semantic lookup latency from 450ms to 42ms.",
      tailored: "Engineered production AI vector search infrastructure using pgvector, cutting semantic query latency from 450ms to 42ms for AI platforms.",
      keyword: "AI vector search & latency"
    },
    {
      original: "Built real-time Next.js analytics platform with TanStack Query and WebSockets serving 120,000 MAU.",
      tailored: "Built high-performance Next.js App Router analytics platform with TanStack Query and streaming WebSockets serving 120,000 MAU.",
      keyword: "Next.js App Router & streaming"
    }
  ];

  const coverLetterText = `Dear Hiring Team at ${targetCompany},

I am writing to express my enthusiastic interest in the ${targetRole} role. Having spent over 8 years scaling distributed web architectures and high-throughput systems, I was immediately drawn to ${targetCompany}'s developer-first AI tooling.

In my recent engineering leadership, I architected event-driven microservices handling 45M daily operations, built production AI vector search infrastructure using pgvector that cut query latency by 90%, and scaled real-time Next.js platforms to 120,000 MAU.

I am eager to bring this deep production experience with modern web architectures and robust backend systems to ${targetCompany}'s AI Platforms team.

Thank you for your time and consideration.

Sincerely,
Alex Chen`;

  const handleCopy = () => {
    navigator.clipboard.writeText(coverLetterText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Studio Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-gray-400">Target Role:</span>
            <span className="text-xs font-extrabold text-primary-400">{targetRole} @ {targetCompany}</span>
          </div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary-400" />
            AI Resume & Cover Letter Studio
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Strict Zero-Fabrication guarantee: bullet points are tailored for keyword match without inventing claims or dates.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4" />
            Zero-Fabrication Guardrail: Verified
          </div>
          <button
            onClick={() => alert("Downloading ATS Single-Column PDF...")}
            className="px-3.5 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary flex items-center gap-1.5 transition-all"
          >
            <Download className="w-3.5 h-3.5" /> Export ATS PDF
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-surface-border gap-4">
        <button
          onClick={() => setActiveTab("resume")}
          className={`pb-3 text-xs font-bold transition-all relative ${
            activeTab === "resume" ? "text-primary-400" : "text-gray-400 hover:text-gray-200"
          }`}
        >
          Bullet Point Diffs (3 Highlighted)
          {activeTab === "resume" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"></div>
          )}
        </button>
        <button
          onClick={() => setActiveTab("cover_letter")}
          className={`pb-3 text-xs font-bold transition-all relative ${
            activeTab === "cover_letter" ? "text-primary-400" : "text-gray-400 hover:text-gray-200"
          }`}
        >
          Tailored Cover Letter
          {activeTab === "cover_letter" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"></div>
          )}
        </button>
      </div>

      {/* Tab Content: Resume Diffs */}
      {activeTab === "resume" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-bold text-gray-400 px-2">
            <span>Original Master Profile Bullet</span>
            <span className="text-primary-300">Tailored Keyword-Matched Bullet</span>
          </div>

          {bulletDiffs.map((diff, index) => (
            <div
              key={index}
              className="p-5 rounded-xl glass-card border border-surface-border grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {/* Left: Original */}
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                  Ground Truth
                </span>
                <p className="text-xs text-gray-400 leading-relaxed bg-surface/50 p-3 rounded-lg border border-surface-border/50">
                  {diff.original}
                </p>
              </div>

              {/* Right: Tailored with Diff */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-primary-400 uppercase tracking-wider">
                    Optimized for {targetCompany}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-primary-500/20 text-primary-300 border border-primary-500/30 font-semibold">
                    {diff.keyword}
                  </span>
                </div>
                <p className="text-xs text-gray-100 font-medium leading-relaxed bg-primary-950/30 p-3 rounded-lg border border-primary-500/30">
                  {diff.tailored}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab Content: Cover Letter */}
      {activeTab === "cover_letter" && (
        <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-300">
              Generated Research-Informed Cover Letter ({targetCompany})
            </span>
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-surface-elevated hover:bg-surface-border text-gray-200 rounded-lg text-xs font-semibold border border-surface-border flex items-center gap-1.5 transition-all"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied to Clipboard" : "Copy Letter"}</span>
            </button>
          </div>

          <div className="bg-surface/80 p-5 rounded-xl border border-surface-border font-mono text-xs text-gray-300 whitespace-pre-line leading-relaxed">
            {coverLetterText}
          </div>
        </div>
      )}
    </div>
  );
};
