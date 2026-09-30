"use client";

import React, { useState } from "react";
import { 
  Globe2, 
  Activity, 
  CheckCircle2, 
  PauseCircle, 
  PlayCircle, 
  Plus, 
  RefreshCw, 
  Search, 
  Sparkles, 
  ExternalLink, 
  ShieldCheck, 
  Code, 
  Database,
  Sliders,
  X,
  Check
} from "lucide-react";

export const SourcesAdminView: React.FC = () => {
  const [sources, setSources] = useState([
    {
      id: "greenhouse",
      name: "Greenhouse ATS Public Board",
      type: "ats",
      layer: "Layer 2: ATS",
      legalStatus: "official_api",
      countries: ["GLOBAL"],
      rateLimit: 120,
      refreshHours: 4,
      isPaused: false,
      totalJobs: "420,000",
      status: "healthy"
    },
    {
      id: "lever",
      name: "Lever ATS Public Postings",
      type: "ats",
      layer: "Layer 2: ATS",
      legalStatus: "official_api",
      countries: ["GLOBAL"],
      rateLimit: 120,
      refreshHours: 4,
      isPaused: false,
      totalJobs: "185,000",
      status: "healthy"
    },
    {
      id: "ashby",
      name: "Ashby ATS Public Board",
      type: "ats",
      layer: "Layer 2: ATS",
      legalStatus: "official_api",
      countries: ["GLOBAL"],
      rateLimit: 100,
      refreshHours: 4,
      isPaused: false,
      totalJobs: "94,000",
      status: "healthy"
    },
    {
      id: "adzuna",
      name: "Adzuna Global Job Search API",
      type: "api",
      layer: "Layer 1: Aggregator",
      legalStatus: "official_api",
      countries: ["US", "GB", "DE", "FR", "CA", "AU", "IN"],
      rateLimit: 60,
      refreshHours: 6,
      isPaused: false,
      totalJobs: "640,000",
      status: "healthy"
    },
    {
      id: "remotive",
      name: "Remotive Remote Community Feed",
      type: "feed",
      layer: "Layer 1: Remote",
      legalStatus: "public_feed",
      countries: ["GLOBAL"],
      rateLimit: 60,
      refreshHours: 4,
      isPaused: false,
      totalJobs: "28,500",
      status: "healthy"
    },
    {
      id: "himalayas",
      name: "Himalayas Remote (Config-Driven)",
      type: "feed",
      layer: "Layer 1: Declarative JSON",
      legalStatus: "public_feed",
      countries: ["GLOBAL"],
      rateLimit: 60,
      refreshHours: 6,
      isPaused: false,
      totalJobs: "14,200",
      status: "healthy"
    }
  ]);

  // Detector state
  const [detectUrl, setDetectUrl] = useState("https://boards.greenhouse.io/vercel");
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectedResult, setDetectedResult] = useState<any>(null);

  // Test crawl modal state
  const [testModalData, setTestModalData] = useState<any>(null);
  const [isTestingSource, setIsTestingSource] = useState(false);

  // New source modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSourceJson, setNewSourceJson] = useState(`{
  "source_id": "weworkremotely",
  "name": "We Work Remotely Feed",
  "source_type": "feed",
  "endpoint_url": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
  "refresh_interval_hours": 6
}`);

  const handleTogglePause = (sourceId: string) => {
    setSources(prev => prev.map(s => s.id === sourceId ? { ...s, isPaused: !s.isPaused } : s));
  };

  const handleRunDetector = () => {
    setIsDetecting(true);
    setTimeout(() => {
      setIsDetecting(false);
      let ats = "custom_web";
      let slug = "company";
      if (detectUrl.includes("greenhouse.io")) { ats = "greenhouse"; slug = "vercel"; }
      else if (detectUrl.includes("lever.co")) { ats = "lever"; slug = "linear"; }
      else if (detectUrl.includes("ashbyhq.com")) { ats = "ashby"; slug = "ramp"; }
      else if (detectUrl.includes("workday")) { ats = "workday"; slug = "enterprise"; }

      setDetectedResult({
        atsType: ats,
        companySlug: slug,
        careersUrl: detectUrl,
        directApiUrl: ats === "greenhouse" ? `https://boards-api.greenhouse.io/v1/boards/${slug}/jobs` : `https://api.lever.co/v0/postings/${slug}`,
        confidence: 0.98,
        detectionMethod: "url_signature"
      });
    }, 700);
  };

  const handleTestCrawl = (s: any) => {
    setIsTestingSource(true);
    setTimeout(() => {
      setIsTestingSource(false);
      setTestModalData({
        source: s.name,
        sourceId: s.id,
        jobsFetched: 20,
        latencyMs: 84.5,
        samples: [
          { title: "Staff Software Engineer, Platforms", company: "Vercel", location: "Remote (US)", salary: "$175,000 - $215,000" },
          { title: "Principal Distributed Systems Architect", company: "Vercel", location: "Remote (Worldwide)", salary: "$190,000 - $240,000" }
        ]
      });
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Globe2 className="w-5 h-5 text-primary-400" />
            Global Job Coverage Layer & Source Registry
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Autonomous multi-layer crawler indexing official APIs, public ATS endpoints, and structured JSON-LD schemas worldwide.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary flex items-center gap-1.5 transition-all"
        >
          <Plus className="w-4 h-4" />
          Add Source (YAML / JSON)
        </button>
      </div>

      {/* Planetary Scale KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="text-[11px] text-gray-400 mb-1 flex items-center justify-between">
            <span>Global Active Jobs</span>
            <Database className="w-3.5 h-3.5 text-primary-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">1,248,910</div>
          <div className="text-[10px] text-emerald-400 mt-1">14,200 new jobs/hr</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="text-[11px] text-gray-400 mb-1 flex items-center justify-between">
            <span>Indexed Companies</span>
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">52,400</div>
          <div className="text-[10px] text-gray-400 mt-1">Wikidata + Subdomain discovery</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="text-[11px] text-gray-400 mb-1 flex items-center justify-between">
            <span>Global Countries</span>
            <Globe2 className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-300">104</div>
          <div className="text-[10px] text-gray-400 mt-1">54 supported languages</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="text-[11px] text-gray-400 mb-1 flex items-center justify-between">
            <span>Freshness Compliance</span>
            <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-amber-300">99.4%</div>
          <div className="text-[10px] text-gray-400 mt-1">Verified 404 auto-purge</div>
        </div>
      </div>

      {/* ATS Detector Playground */}
      <div className="p-5 rounded-2xl glass-card border border-surface-border space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary-400" />
            <h3 className="text-sm font-bold text-white">Universal ATS Detector & Careers Sniffer</h3>
          </div>
          <span className="text-[10px] text-gray-400">Layer 2 Auto-Detection</span>
        </div>
        <p className="text-xs text-gray-400">
          Enter any company website or career portal. JobPilot evaluates network signatures, iframes, and scripts to attach the zero-scraping public API connector.
        </p>

        <div className="flex gap-2">
          <input
            type="text"
            value={detectUrl}
            onChange={(e) => setDetectUrl(e.target.value)}
            placeholder="e.g. https://jobs.lever.co/linear or stripe.com"
            className="flex-1 px-3.5 py-2 bg-surface border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500 font-mono"
          />
          <button
            onClick={handleRunDetector}
            disabled={isDetecting}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shrink-0"
          >
            {isDetecting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            <span>Detect ATS</span>
          </button>
        </div>

        {detectedResult && (
          <div className="p-3.5 rounded-xl bg-surface border border-primary-500/30 text-xs text-gray-300 space-y-1 mt-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" /> Detected ATS Engine:{" "}
                <span className="uppercase text-primary-300 font-extrabold">{detectedResult.atsType}</span>
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                {Math.round(detectedResult.confidence * 100)}% Confidence
              </span>
            </div>
            <div className="text-[11px] text-gray-400">
              Company Slug: <span className="text-gray-200 font-mono">{detectedResult.companySlug}</span> • Detection: {detectedResult.detectionMethod}
            </div>
            {detectedResult.directApiUrl && (
              <div className="text-[10px] text-primary-400 font-mono truncate">
                Direct Ingestion Endpoint: {detectedResult.directApiUrl}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Source Registry Table */}
      <div className="p-5 rounded-2xl glass-card border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white">Active Source Connectors & Registry</h3>
            <p className="text-xs text-gray-400 mt-0.5">Plug-and-play connectors with circuit breakers and rate limiters.</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-surface-border text-gray-400 font-semibold text-[11px]">
                <th className="pb-3 pl-2">Source Connector</th>
                <th className="pb-3">Ingestion Layer</th>
                <th className="pb-3">Legal Status</th>
                <th className="pb-3">Rate Limit</th>
                <th className="pb-3">Indexed Jobs</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right pr-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border/50 text-gray-200">
              {sources.map((s) => (
                <tr key={s.id} className="hover:bg-surface-elevated/40 transition-colors">
                  <td className="py-3 pl-2 font-bold text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span>{s.name}</span>
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-primary-500/10 text-primary-300 border border-primary-500/20">
                      {s.layer}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                      {s.legalStatus}
                    </span>
                  </td>
                  <td className="py-3 text-[11px] text-gray-400">{s.rateLimit} req/min</td>
                  <td className="py-3 font-semibold text-white">{s.totalJobs}</td>
                  <td className="py-3">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      s.isPaused ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    }`}>
                      {s.isPaused ? "PAUSED" : "ACTIVE"}
                    </span>
                  </td>
                  <td className="py-3 text-right pr-2 space-x-2">
                    <button
                      onClick={() => handleTestCrawl(s)}
                      className="px-2.5 py-1 bg-surface-elevated hover:bg-surface-border border border-surface-border rounded text-[10px] font-semibold text-gray-300 transition-all"
                    >
                      Test Run
                    </button>
                    <button
                      onClick={() => handleTogglePause(s.id)}
                      className={`px-2 py-1 rounded text-[10px] font-semibold border transition-all ${
                        s.isPaused
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                          : "bg-surface-elevated text-gray-400 hover:text-white border-surface-border"
                      }`}
                    >
                      {s.isPaused ? "Resume" : "Pause"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Test Output Modal */}
      {testModalData && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-glass">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Connector Crawl Test: {testModalData.source}
                </h3>
                <p className="text-xs text-gray-400">Response time: {testModalData.latencyMs}ms • 20 jobs fetched</p>
              </div>
              <button
                onClick={() => setTestModalData(null)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-elevated"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2">
              <span className="text-xs font-bold text-gray-300">Normalized Schema Samples:</span>
              {testModalData.samples.map((job: any, i: number) => (
                <div key={i} className="p-3 rounded-lg bg-surface-elevated border border-surface-border text-xs space-y-0.5">
                  <div className="font-bold text-white">{job.title}</div>
                  <div className="text-[11px] text-gray-400">{job.company} • {job.location} • {job.salary}</div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setTestModalData(null)}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Config-Driven Source Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-glass">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Code className="w-4 h-4 text-primary-400" />
                  Add New Source (Declarative JSON / YAML)
                </h3>
                <p className="text-xs text-gray-400">Declare endpoint and field mappings. Registered instantly in SourceRegistry without code.</p>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-elevated"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <textarea
              rows={8}
              value={newSourceJson}
              onChange={(e) => setNewSourceJson(e.target.value)}
              className="w-full p-3.5 bg-background border border-surface-border rounded-xl text-xs text-emerald-300 font-mono leading-relaxed focus:outline-none focus:border-primary-500"
            />

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 bg-surface-elevated text-gray-300 rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  alert("New source registered into JobPilot SourceRegistry successfully!");
                  setShowAddModal(false);
                }}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary"
              >
                Register Source
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
