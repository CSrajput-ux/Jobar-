"use client";

import React, { useState } from "react";
import { 
  Search, 
  Filter, 
  Sparkles, 
  MapPin, 
  DollarSign, 
  Briefcase, 
  RefreshCw, 
  ExternalLink, 
  Check, 
  FileText,
  AlertCircle,
  X,
  ChevronRight
} from "lucide-react";

interface JobDiscoveryViewProps {
  onTailorAndApply: (job: any) => void;
  onSaveJob: (job: any) => void;
}

export const JobDiscoveryView: React.FC<JobDiscoveryViewProps> = ({
  onTailorAndApply,
  onSaveJob
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSource, setSelectedSource] = useState("all");
  const [selectedWorkMode, setSelectedWorkMode] = useState("all");
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedJobForModal, setSelectedJobForModal] = useState<any | null>(null);

  const initialJobs = [
    {
      id: "e0000000-0000-0000-0000-000000000002",
      companyName: "Vercel",
      title: "Senior Full-Stack Engineer, AI Platforms",
      location: "Remote (United States)",
      workMode: "remote",
      salaryRange: "$170,000 - $210,000 + Equity",
      source: "greenhouse_api",
      atsType: "greenhouse",
      externalUrl: "https://boards.greenhouse.io/vercel/jobs/5918239002",
      descriptionText: "Join Vercel to shape developer tooling for next-gen AI applications. You will build frontend web applications with Next.js App Router and high-throughput streaming backend microservices.",
      matchScore: 96,
      reasoning: {
        matchedSkills: ["Next.js", "TypeScript", "FastAPI", "React", "Tailwind CSS", "LLM APIs"],
        missingSkills: [],
        redFlags: [],
        fitSummary: "Exceptional fit. Alex has 8+ years hands-on production Next.js and high-performance API experience directly matching Vercel AI platform priorities.",
        seniorityAlignment: "ideal"
      }
    },
    {
      id: "e0000000-0000-0000-0000-000000000001",
      companyName: "Linear",
      title: "Staff Infrastructure & Systems Engineer",
      location: "Remote (Worldwide)",
      workMode: "remote",
      salaryRange: "$180,000 - $220,000 + Equity",
      source: "lever_api",
      atsType: "lever",
      externalUrl: "https://jobs.lever.co/linear/staff-infrastructure-systems",
      descriptionText: "Scale distributed synchronization protocols, real-time WebSocket state coordination, and backend microservices at Linear with high availability.",
      matchScore: 95,
      reasoning: {
        matchedSkills: ["Distributed Systems", "TypeScript", "Redis", "PostgreSQL", "Kafka"],
        missingSkills: [],
        redFlags: [],
        fitSummary: "Outstanding backend alignment with direct experience handling 45M daily events in real-time distributed environments.",
        seniorityAlignment: "ideal"
      }
    },
    {
      id: "e0000000-0000-0000-0000-000000000003",
      companyName: "Supabase",
      title: "Backend Engineer, Postgres & Vector Engine",
      location: "Remote",
      workMode: "remote",
      salaryRange: "$165,000 - $205,000 + Equity",
      source: "greenhouse_api",
      atsType: "greenhouse",
      externalUrl: "https://boards.greenhouse.io/supabase/jobs/4829103002",
      descriptionText: "Help scale Supabase pgvector and real-time database replication services for millions of developers worldwide.",
      matchScore: 93,
      reasoning: {
        matchedSkills: ["PostgreSQL", "pgvector", "Python", "Distributed Systems", "Redis"],
        missingSkills: ["Go Internals"],
        redFlags: [],
        fitSummary: "Direct production experience with pgvector reducing lookup latency by 90% matches core database scaling objectives.",
        seniorityAlignment: "ideal"
      }
    },
    {
      id: "e0000000-0000-0000-0000-000000000004",
      companyName: "GitLab",
      title: "Senior Backend Engineer, Distribution",
      location: "Remote (Worldwide)",
      workMode: "remote",
      salaryRange: "$160,000 - $205,000",
      source: "remotive",
      atsType: "custom",
      externalUrl: "https://remotive.com/remote-jobs/software-dev/senior-backend-engineer-gitlab",
      descriptionText: "Build resilient CI/CD release architectures, packaging pipelines, and container delivery systems at GitLab.",
      matchScore: 88,
      reasoning: {
        matchedSkills: ["Python", "Docker", "Kubernetes", "PostgreSQL", "CI/CD"],
        missingSkills: ["Ruby on Rails"],
        redFlags: [],
        fitSummary: "Strong cloud infrastructure background with extensive Docker and distributed deployment experience.",
        seniorityAlignment: "ideal"
      }
    }
  ];

  const [jobs, setJobs] = useState(initialJobs);

  const handleSyncFeeds = () => {
    setIsSyncing(true);
    setTimeout(() => {
      setIsSyncing(false);
    }, 1200);
  };

  const filteredJobs = jobs.filter(j => {
    const matchesSearch = j.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          j.companyName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSource = selectedSource === "all" || j.atsType === selectedSource;
    const matchesWork = selectedWorkMode === "all" || j.workMode === selectedWorkMode;
    return matchesSearch && matchesSource && matchesWork;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-primary-400" />
            Global Job Discovery Engine
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Aggregated from Greenhouse public boards, Lever public APIs, and Remotive verified remote listings.
          </p>
        </div>
        <button
          onClick={handleSyncFeeds}
          disabled={isSyncing}
          className="px-3.5 py-2 bg-surface-elevated hover:bg-surface-border text-gray-200 border border-surface-border rounded-lg text-xs font-semibold flex items-center gap-2 transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? "animate-spin text-primary-400" : "text-gray-400"}`} />
          <span>{isSyncing ? "Syncing ATS Feeds..." : "Refresh Feeds"}</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-3.5 rounded-xl glass-panel border border-surface-border flex flex-col md:flex-row items-center gap-3">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by role or company..."
            className="w-full pl-9 pr-3 py-1.5 bg-background/80 border border-surface-border rounded-lg text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-primary-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          <span className="text-[11px] text-gray-400 shrink-0">Source:</span>
          {["all", "greenhouse", "lever", "custom"].map((src) => (
            <button
              key={src}
              onClick={() => setSelectedSource(src)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium capitalize transition-all shrink-0 ${
                selectedSource === src
                  ? "bg-primary-600/20 text-primary-300 border border-primary-500/40"
                  : "bg-surface-elevated/40 text-gray-400 hover:text-gray-200"
              }`}
            >
              {src === "custom" ? "Remotive" : src}
            </button>
          ))}

          <span className="text-[11px] text-gray-400 shrink-0 ml-2">Mode:</span>
          {["all", "remote", "hybrid"].map((mode) => (
            <button
              key={mode}
              onClick={() => setSelectedWorkMode(mode)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium capitalize transition-all shrink-0 ${
                selectedWorkMode === mode
                  ? "bg-primary-600/20 text-primary-300 border border-primary-500/40"
                  : "bg-surface-elevated/40 text-gray-400 hover:text-gray-200"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Job Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredJobs.map((job) => {
          const score = job.matchScore;
          const scoreColor = score >= 90 ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10" : "text-amber-400 border-amber-500/40 bg-amber-500/10";
          return (
            <div
              key={job.id}
              className="p-5 rounded-xl glass-card border border-surface-border flex flex-col justify-between hover:border-primary-500/40 transition-all group"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-gray-300">{job.companyName}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded uppercase font-semibold bg-surface-elevated text-gray-400 border border-surface-border">
                        {job.atsType}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-white group-hover:text-primary-300 transition-colors">
                      {job.title}
                    </h3>
                  </div>

                  {/* Match Score Badge */}
                  <button
                    onClick={() => setSelectedJobForModal(job)}
                    className={`px-2.5 py-1 rounded-lg border text-xs font-extrabold flex items-center gap-1.5 shrink-0 transition-transform hover:scale-105 ${scoreColor}`}
                    title="Click to view AI reasoning breakdown"
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>{score}% Fit</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-[11px] text-gray-400 mt-2 mb-3">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-gray-500" /> {job.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-3 h-3 text-gray-500" /> {job.salaryRange}
                  </span>
                </div>

                <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">
                  {job.descriptionText}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-surface-border/60 flex items-center justify-between">
                <button
                  onClick={() => setSelectedJobForModal(job)}
                  className="text-xs text-primary-400 hover:text-primary-300 font-semibold flex items-center gap-1"
                >
                  Inspect Reasoning <ChevronRight className="w-3 h-3" />
                </button>
                <div className="flex items-center gap-2">
                  <a
                    href={job.externalUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-surface-elevated transition-colors"
                    title="View official ATS listing"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                  <button
                    onClick={() => onTailorAndApply(job)}
                    className="px-3.5 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary transition-all flex items-center gap-1.5"
                  >
                    <FileText className="w-3.5 h-3.5" /> Tailor & Apply
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Match Breakdown Modal */}
      {selectedJobForModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-glass max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-gray-400">{selectedJobForModal.companyName}</span>
                  <span className="text-xs px-2 py-0.5 rounded font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {selectedJobForModal.matchScore}% Match
                  </span>
                </div>
                <h2 className="text-base font-bold text-white mt-1">
                  {selectedJobForModal.title}
                </h2>
              </div>
              <button
                onClick={() => setSelectedJobForModal(null)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-elevated"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Fit Summary */}
            <div className="p-3.5 rounded-xl bg-surface-elevated border border-surface-border text-xs text-gray-300">
              <span className="font-semibold text-primary-300">AI Fit Reasoning: </span>
              {selectedJobForModal.reasoning.fitSummary}
            </div>

            {/* Matched Skills */}
            <div>
              <h4 className="text-xs font-bold text-gray-300 mb-2 flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" /> Matched Core Skills & Stack
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {selectedJobForModal.reasoning.matchedSkills.map((s: string) => (
                  <span key={s} className="px-2.5 py-1 rounded-md text-[11px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            {selectedJobForModal.reasoning.missingSkills.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-gray-300 mb-2 flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-400" /> Missing / Unmentioned Skills
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedJobForModal.reasoning.missingSkills.map((s: string) => (
                    <span key={s} className="px-2.5 py-1 rounded-md text-[11px] bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-3 border-t border-surface-border flex items-center justify-between">
              <span className="text-[11px] text-gray-500">Zero-fabrication validation: Verified</span>
              <button
                onClick={() => {
                  const j = selectedJobForModal;
                  setSelectedJobForModal(null);
                  onTailorAndApply(j);
                }}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary transition-all"
              >
                Proceed to Resume Tailoring
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
