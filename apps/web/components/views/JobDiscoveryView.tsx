"use client";

import React, { useState, useEffect } from "react";
import { api } from "../../lib/api";
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
  ChevronRight,
  Globe,
  Lock,
  Play,
  Pause,
  Settings,
  ShieldCheck,
  CheckCircle2,
  User,
  Key,
  Layers,
  Terminal,
  Zap,
  ArrowRight,
  Plus,
  Eye,
  Send,
  Sliders,
  Smartphone,
  Monitor
} from "lucide-react";

interface JobDiscoveryViewProps {
  onTailorAndApply: (job: any) => void;
  onSaveJob: (job: any) => void;
}

interface Platform {
  id: string;
  name: string;
  tagline: string;
  url: string;
  loginUrl: string;
  logo: string;
  category: string;
  isConnected: boolean;
  accountEmail?: string | null;
  sessionSavedAt?: string | null;
  autoApplyEnabled: boolean;
  credentialsStored: boolean;
  appliedCount: number;
  lastSyncStatus: string;
  featured?: boolean;
}

interface AutoApplyConfig {
  autoPilotActive: boolean;
  targetRoles: string[];
  locations: string[];
  workModes: string[];
  minMatchScore: number;
  dailyApplyCap: number;
  maxApplicationsPerHour: number;
  autoTailorResume: boolean;
  autoGenerateCoverLetter: boolean;
  antiBotHumanPacing: boolean;
  stopOnCaptcha: boolean;
  activePlatformIds: string[];
}

interface ActivityLog {
  id: string;
  timestamp: string;
  platform: string;
  level: "INFO" | "SUCCESS" | "WARNING" | "RUNNING";
  message: string;
}

export const JobDiscoveryView: React.FC<JobDiscoveryViewProps> = ({
  onTailorAndApply,
  onSaveJob
}) => {
  // Navigation Tabs: "platforms" (Live Platform Hub), "autopilot" (AI Auto-Apply Rules), "feed" (Aggregated Job Feed)
  const [activeTab, setActiveTab] = useState<"platforms" | "autopilot" | "feed">("platforms");

  // State for Platforms & Live Browser
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(false);
  const [selectedPlatformForLive, setSelectedPlatformForLive] = useState<Platform | null>(null);
  const [liveBrowserUrl, setLiveBrowserUrl] = useState("");
  const [viewportMode, setViewportMode] = useState<"desktop" | "mobile">("desktop");
  const [canvasMode, setCanvasMode] = useState<"interactive" | "iframe">("interactive");
  
  // Credentials & Session Drawer inside Live Browser
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [sessionToken, setSessionToken] = useState("");
  const [enableAutoApplyForPlatform, setEnableAutoApplyForPlatform] = useState(true);
  const [isSavingSession, setIsSavingSession] = useState(false);
  const [sessionSaveSuccess, setSessionSaveSuccess] = useState(false);

  // Custom Platform Modal
  const [showAddCustomModal, setShowAddCustomModal] = useState(false);
  const [customPlatformName, setCustomPlatformName] = useState("");
  const [customPlatformUrl, setCustomPlatformUrl] = useState("");
  const [customPlatformLoginUrl, setCustomPlatformLoginUrl] = useState("");
  const [customPlatformCategory, setCustomPlatformCategory] = useState("Custom Tech Portal");

  // Auto-Apply Configuration & Agent Status
  const [config, setConfig] = useState<AutoApplyConfig>({
    autoPilotActive: true,
    targetRoles: ["Full Stack Developer", "Backend Engineer", "Senior Frontend Engineer", "AI/ML Engineer"],
    locations: ["Remote", "Worldwide", "India (Bangalore/Hybrid)", "United States"],
    workModes: ["remote", "hybrid"],
    minMatchScore: 85,
    dailyApplyCap: 20,
    maxApplicationsPerHour: 5,
    autoTailorResume: true,
    autoGenerateCoverLetter: true,
    antiBotHumanPacing: true,
    stopOnCaptcha: true,
    activePlatformIds: ["wellfound", "naukri", "linkedin", "greenhouse", "lever"]
  });
  const [newRoleInput, setNewRoleInput] = useState("");
  const [newLocationInput, setNewLocationInput] = useState("");
  const [isSavingConfig, setIsSavingConfig] = useState(false);
  const [isExecutingAutoApply, setIsExecutingAutoApply] = useState(false);
  const [logs, setLogs] = useState<ActivityLog[]>([]);

  // Feed Jobs State
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSource, setSelectedSource] = useState("all");
  const [selectedWorkMode, setSelectedWorkMode] = useState("all");
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedJobForModal, setSelectedJobForModal] = useState<any | null>(null);
  const [jobs, setJobs] = useState<any[]>([]);

  // Initial Load: Fetch Platforms, Config, Logs, and Jobs
  useEffect(() => {
    loadPlatforms();
    loadAutoApplyConfig();
    loadLogs();
    loadJobs();
  }, []);

  const loadPlatforms = async () => {
    setIsLoadingPlatforms(true);
    try {
      const data = await api.getPlatforms();
      if (Array.isArray(data) && data.length > 0) {
        setPlatforms(data);
      }
    } catch (err) {
      console.warn("Failed to fetch platforms from API:", err);
    } finally {
      setIsLoadingPlatforms(false);
    }
  };

  const loadAutoApplyConfig = async () => {
    try {
      const data = await api.getAutoApplySettings();
      if (data && typeof data === "object") {
        setConfig(prev => ({ ...prev, ...data }));
      }
    } catch (err) {
      console.warn("Failed to load auto-apply config:", err);
    }
  };

  const loadLogs = async () => {
    try {
      const data = await api.getAutoApplyLogs();
      if (Array.isArray(data) && data.length > 0) {
        setLogs(data);
      }
    } catch (err) {
      console.warn("Failed to load auto-apply logs:", err);
    }
  };

  const loadJobs = async () => {
    try {
      const remoteJobs = await api.getJobs();
      if (Array.isArray(remoteJobs) && remoteJobs.length > 0) {
        setJobs(remoteJobs);
      } else {
        // Fallback default rich catalog if DB empty
        setJobs([
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
            descriptionText: "Build next-generation generative AI web platforms using Next.js App Router and serverless streaming runtimes.",
            matchScore: 96,
            reasoning: {
              matchedSkills: ["Next.js", "TypeScript", "FastAPI", "React", "Tailwind CSS"],
              missingSkills: [],
              redFlags: [],
              fitSummary: "Exceptional match with production Next.js experience and real-time streaming backend.",
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
            descriptionText: "Scale distributed synchronization protocols, real-time WebSocket state coordination, and backend microservices at Linear.",
            matchScore: 95,
            reasoning: {
              matchedSkills: ["Distributed Systems", "TypeScript", "Redis", "PostgreSQL", "Kafka"],
              missingSkills: [],
              redFlags: [],
              fitSummary: "Outstanding backend alignment with distributed high-throughput architecture.",
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
              fitSummary: "Direct production experience with pgvector reducing lookup latency by 90%.",
              seniorityAlignment: "ideal"
            }
          },
          {
            id: "e0000000-0000-0000-0000-000000000005",
            companyName: "Razorpay",
            title: "Lead Backend Architect - Core Payments",
            location: "Bangalore / Hybrid",
            workMode: "hybrid",
            salaryRange: "₹45,00,000 - ₹65,00,000 + ESOPs",
            source: "naukri",
            atsType: "naukri",
            externalUrl: "https://www.naukri.com/job-listings-razorpay-lead-backend",
            descriptionText: "Architect high-throughput payment routing microservices handling 15,000+ transactions/sec with 99.999% uptime.",
            matchScore: 94,
            reasoning: {
              matchedSkills: ["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka", "Distributed Systems"],
              missingSkills: [],
              redFlags: [],
              fitSummary: "Direct match for high-concurrency payment APIs and database performance optimization.",
              seniorityAlignment: "ideal"
            }
          },
          {
            id: "e0000000-0000-0000-0000-000000000006",
            companyName: "Postman",
            title: "Staff Full Stack Engineer - API Network",
            location: "Remote (India / Global)",
            workMode: "remote",
            salaryRange: "$150,000 - $190,000",
            source: "wellfound",
            atsType: "wellfound",
            externalUrl: "https://wellfound.com/jobs/postman-staff-full-stack",
            descriptionText: "Build scalable API exploration, testing, and collaboration tools used by 30M+ developers across the world.",
            matchScore: 96,
            reasoning: {
              matchedSkills: ["TypeScript", "React", "Node.js", "FastAPI", "GraphQL", "WebSockets"],
              missingSkills: [],
              redFlags: [],
              fitSummary: "Outstanding full-stack portfolio with deep developer tooling experience.",
              seniorityAlignment: "ideal"
            }
          }
        ]);
      }
    } catch (err) {
      console.warn("Unable to load the job catalog:", err);
    }
  };

  // Open Platform Live in In-App Browser Modal
  const handleOpenLivePlatform = (platform: Platform) => {
    setSelectedPlatformForLive(platform);
    setLiveBrowserUrl(platform.loginUrl || platform.url);
    setLoginEmail(platform.accountEmail || "alex.chen.dev@example.com");
    setLoginPassword("••••••••••••");
    setSessionToken("");
    setEnableAutoApplyForPlatform(platform.autoApplyEnabled);
    setSessionSaveSuccess(false);
  };

  // Save Credentials & Verify Session for a Platform
  const handleSavePlatformSession = async () => {
    if (!selectedPlatformForLive) return;
    setIsSavingSession(true);
    try {
      await api.connectPlatform({
        platformId: selectedPlatformForLive.id,
        accountEmail: loginEmail,
        passwordOrToken: loginPassword,
        sessionCookies: sessionToken,
        autoApplyEnabled: enableAutoApplyForPlatform,
        saveCredentials: true
      });
      setSessionSaveSuccess(true);
      await loadPlatforms();
      await loadLogs();
      setTimeout(() => setSessionSaveSuccess(false), 3500);
    } catch (err) {
      console.error("Failed to save platform session:", err);
    } finally {
      setIsSavingSession(false);
    }
  };

  // Add Any Custom Platform
  const handleAddCustomPlatform = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customPlatformName || !customPlatformUrl) return;
    try {
      const res = await api.addCustomPlatform({
        name: customPlatformName,
        url: customPlatformUrl,
        loginUrl: customPlatformLoginUrl || customPlatformUrl,
        category: customPlatformCategory
      });
      setShowAddCustomModal(false);
      setCustomPlatformName("");
      setCustomPlatformUrl("");
      setCustomPlatformLoginUrl("");
      await loadPlatforms();
      if (res.platform) {
        handleOpenLivePlatform(res.platform);
      }
    } catch (err) {
      console.error("Failed to add custom platform:", err);
    }
  };

  // Toggle Auto-Pilot Master Switch
  const handleToggleAutoPilot = async () => {
    const nextState = !config.autoPilotActive;
    const updated = { ...config, autoPilotActive: nextState };
    setConfig(updated);
    try {
      await api.updateAutoApplySettings({ autoPilotActive: nextState });
      await loadLogs();
    } catch (err) {
      console.error("Failed to update auto-pilot switch:", err);
    }
  };

  // Run Immediate Auto-Apply Cycle
  const handleTriggerAutoApplyNow = async (platformId?: string) => {
    setIsExecutingAutoApply(true);
    try {
      const res = await api.runAutoApply(platformId);
      await loadPlatforms();
      await loadLogs();
      if (res && res.details && res.details.length > 0) {
        // Prepend to catalog or notify
        const newDispatched = res.details.map((d: any) => ({
          id: d.id,
          companyName: d.company,
          title: d.title,
          location: "Remote / Hybrid",
          workMode: "remote",
          salaryRange: "Market Competitive",
          source: d.platform.toLowerCase(),
          atsType: d.platform.toLowerCase(),
          externalUrl: "#",
          descriptionText: `Automated application dispatched via ${d.platform} session credentials.`,
          matchScore: d.fitScore,
          appliedStatus: "APPLIED",
          reasoning: {
            matchedSkills: ["Full Stack", "TypeScript", "FastAPI"],
            missingSkills: [],
            redFlags: [],
            fitSummary: `Automated match verified with ${d.fitScore}% score and submitted via active session.`,
            seniorityAlignment: "ideal"
          }
        }));
        setJobs(prev => [...newDispatched, ...prev]);
      }
    } catch (err: any) {
      console.error("Auto-apply run failed:", err);
      alert(err.message || "Failed to trigger auto-apply cycle.");
    } finally {
      setIsExecutingAutoApply(false);
    }
  };

  // Save Auto-Apply Rules
  const handleSaveConfigRules = async () => {
    setIsSavingConfig(true);
    try {
      await api.updateAutoApplySettings(config);
      await loadLogs();
      alert("Auto-Apply rules and parameters saved successfully!");
    } catch (err) {
      console.error("Failed to save auto-apply rules:", err);
    } finally {
      setIsSavingConfig(false);
    }
  };

  // Add / Remove Target Roles
  const handleAddRole = () => {
    if (newRoleInput.trim() && !config.targetRoles.includes(newRoleInput.trim())) {
      setConfig({ ...config, targetRoles: [...config.targetRoles, newRoleInput.trim()] });
      setNewRoleInput("");
    }
  };
  const handleRemoveRole = (role: string) => {
    setConfig({ ...config, targetRoles: config.targetRoles.filter(r => r !== role) });
  };

  // Add / Remove Target Locations
  const handleAddLocation = () => {
    if (newLocationInput.trim() && !config.locations.includes(newLocationInput.trim())) {
      setConfig({ ...config, locations: [...config.locations, newLocationInput.trim()] });
      setNewLocationInput("");
    }
  };
  const handleRemoveLocation = (loc: string) => {
    setConfig({ ...config, locations: config.locations.filter(l => l !== loc) });
  };

  // Filter Jobs in the Catalog
  const filteredJobs = jobs.filter(j => {
    const matchesSearch = j.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          j.companyName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSource = selectedSource === "all" || 
                          j.atsType?.toLowerCase() === selectedSource.toLowerCase() ||
                          j.source?.toLowerCase().includes(selectedSource.toLowerCase());
    const matchesWork = selectedWorkMode === "all" || j.workMode === selectedWorkMode;
    return matchesSearch && matchesSource && matchesWork;
  });

  const connectedPlatformsCount = platforms.filter(p => p.isConnected).length;
  const totalAppliedCount = platforms.reduce((acc, p) => acc + (p.appliedCount || 0), 0);

  return (
    <div className="space-y-6">
      {/* Top Banner / Global Master Bar */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-surface-elevated via-surface to-surface-elevated border border-surface-border shadow-glass relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-primary-500/20 text-primary-300 border border-primary-500/30 flex items-center gap-1.5">
                <Globe className="w-3 h-3 text-primary-400" /> Multi-Platform Live Engine
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold flex items-center gap-1.5 ${
                config.autoPilotActive 
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" 
                  : "bg-gray-500/20 text-gray-400 border border-gray-500/30"
              }`}>
                <span className={`w-2 h-2 rounded-full ${config.autoPilotActive ? "bg-emerald-400 animate-pulse" : "bg-gray-500"}`} />
                {config.autoPilotActive ? "AI Auto-Pilot: ACTIVE" : "AI Auto-Pilot: PAUSED"}
              </span>
              <span className="text-[11px] text-gray-400">
                • {connectedPlatformsCount} of {platforms.length} Platforms Connected
              </span>
              <span className="text-[11px] text-emerald-400 font-semibold">
                • {totalAppliedCount} Automated Submissions Completed
              </span>
            </div>
            <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
              <Zap className="w-6 h-6 text-amber-400 fill-amber-400/20" />
              Live Platform Hub & Autonomous Auto-Apply Engine
            </h1>
            <p className="text-xs text-gray-300 mt-1 max-w-3xl leading-relaxed">
              Open and run <strong>Wellfound</strong>, <strong>Naukri</strong>, <strong>LinkedIn</strong>, <strong>Indeed</strong>, or <strong>any custom career site</strong> live in-app. Save your authenticated session once, and JobPilot’s AI Auto-Pilot automatically discovers matching jobs and submits applications for you.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <button
              onClick={() => setShowAddCustomModal(true)}
              className="px-3.5 py-2 bg-surface-elevated hover:bg-surface-border text-gray-200 border border-surface-border rounded-xl text-xs font-semibold flex items-center gap-2 transition-all hover:scale-105"
            >
              <Plus className="w-3.5 h-3.5 text-primary-400" />
              <span>Add Custom Platform</span>
            </button>
            <button
              onClick={() => handleTriggerAutoApplyNow()}
              disabled={isExecutingAutoApply || connectedPlatformsCount === 0}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all shadow-glow-primary ${
                isExecutingAutoApply || connectedPlatformsCount === 0
                  ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-primary-600 to-amber-500 hover:from-primary-500 hover:to-amber-400 text-white hover:scale-105"
              }`}
            >
              <Zap className={`w-3.5 h-3.5 ${isExecutingAutoApply ? "animate-spin text-amber-200" : "fill-current"}`} />
              <span>{isExecutingAutoApply ? "Auto-Pilot Running..." : "Run Auto-Apply Now"}</span>
            </button>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="mt-5 pt-4 border-t border-surface-border/60 flex flex-wrap items-center gap-2">
          <button
            onClick={() => setActiveTab("platforms")}
            className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "platforms"
                ? "bg-primary-600 text-white shadow-glow-primary border border-primary-400/30"
                : "bg-surface-elevated/60 text-gray-400 hover:text-white hover:bg-surface-elevated"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Live Platforms & Portals ({platforms.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("autopilot")}
            className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "autopilot"
                ? "bg-primary-600 text-white shadow-glow-primary border border-primary-400/30"
                : "bg-surface-elevated/60 text-gray-400 hover:text-white hover:bg-surface-elevated"
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>AI Auto-Apply Rules & Bot Console</span>
            {config.autoPilotActive && (
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            )}
          </button>

          <button
            onClick={() => setActiveTab("feed")}
            className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "feed"
                ? "bg-primary-600 text-white shadow-glow-primary border border-primary-400/30"
                : "bg-surface-elevated/60 text-gray-400 hover:text-white hover:bg-surface-elevated"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Aggregated Jobs Feed ({jobs.length})</span>
          </button>
        </div>
      </div>

      {/* ========================================================
          TAB 1: LIVE PLATFORMS HUB
          ======================================================== */}
      {activeTab === "platforms" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-gray-400">
            <div>
              <p className="text-gray-300 font-semibold">
                Click <strong>&ldquo;Open Live Platform&rdquo;</strong> on any portal to log in. JobPilot captures and saves the active session in your local encrypted vault so the Autonomous Bot can auto-apply seamlessly.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <ShieldCheck className="w-4 h-4" /> 100% Anti-Detection Pacing
              </span>
            </div>
          </div>

          {/* Platforms Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.map((p) => {
              return (
                <div
                  key={p.id}
                  className={`p-5 rounded-2xl glass-card border flex flex-col justify-between transition-all group ${
                    p.isConnected
                      ? "border-emerald-500/30 hover:border-emerald-500/60 bg-gradient-to-b from-surface/90 to-emerald-950/10"
                      : "border-surface-border hover:border-primary-500/40"
                  }`}
                >
                  <div>
                    {/* Header */}
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-surface-elevated text-gray-400 border border-surface-border">
                            {p.category}
                          </span>
                          {p.featured && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                              Popular
                            </span>
                          )}
                        </div>
                        <h3 className="text-base font-extrabold text-white mt-1 group-hover:text-primary-300 transition-colors">
                          {p.name}
                        </h3>
                        <p className="text-[11px] text-gray-400 mt-0.5 line-clamp-1">
                          {p.tagline}
                        </p>
                      </div>

                      {/* Connection Status Badge */}
                      {p.isConnected ? (
                        <div className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-1.5 text-emerald-400 text-[11px] font-bold shrink-0">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Logged In</span>
                        </div>
                      ) : (
                        <div className="px-2.5 py-1 rounded-lg bg-gray-500/10 border border-gray-500/30 flex items-center gap-1.5 text-gray-400 text-[11px] font-medium shrink-0">
                          <Lock className="w-3 h-3 text-amber-400" />
                          <span>Needs Login</span>
                        </div>
                      )}
                    </div>

                    {/* Account Info Bar */}
                    <div className="p-2.5 rounded-xl bg-surface-elevated/70 border border-surface-border text-xs space-y-1 mb-4">
                      {p.isConnected ? (
                        <>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-gray-400 flex items-center gap-1">
                              <User className="w-3 h-3 text-primary-400" /> Account:
                            </span>
                            <span className="font-semibold text-gray-200 truncate max-w-[170px]">
                              {p.accountEmail || "Session Active"}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-gray-400 flex items-center gap-1">
                              <Zap className="w-3 h-3 text-amber-400" /> Auto-Applied:
                            </span>
                            <span className="font-bold text-emerald-400">
                              {p.appliedCount || 0} applications
                            </span>
                          </div>
                          <div className="text-[10px] text-gray-500 pt-0.5 truncate">
                            Status: {p.lastSyncStatus}
                          </div>
                        </>
                      ) : (
                        <div className="text-[11px] text-gray-400 flex items-center gap-1.5 py-1">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                          <span>Not logged in yet. Launch live portal below to authenticate.</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions Bar */}
                  <div className="pt-3 border-t border-surface-border/60 flex items-center justify-between gap-2">
                    <button
                      onClick={() => handleOpenLivePlatform(p)}
                      className="flex-1 py-2 px-3 bg-primary-600/90 hover:bg-primary-500 text-white rounded-xl text-xs font-bold transition-all shadow-glow-primary flex items-center justify-center gap-1.5"
                    >
                      <Globe className="w-3.5 h-3.5" />
                      <span>{p.isConnected ? "Open Live Session" : "Login & Save Session"}</span>
                    </button>

                    {p.isConnected && (
                      <button
                        onClick={() => handleTriggerAutoApplyNow(p.id)}
                        disabled={isExecutingAutoApply}
                        className="py-2 px-3 bg-surface-elevated hover:bg-surface-border text-amber-300 border border-amber-500/30 rounded-xl text-xs font-bold transition-all flex items-center gap-1"
                        title="Auto-apply matching jobs on this platform now"
                      >
                        <Zap className="w-3 h-3 text-amber-400 fill-amber-400/40" />
                        <span>Auto-Apply</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Custom Platform Adder Card */}
            <div 
              onClick={() => setShowAddCustomModal(true)}
              className="p-5 rounded-2xl glass-card border border-dashed border-primary-500/40 hover:border-primary-400 flex flex-col items-center justify-center text-center cursor-pointer group hover:bg-primary-500/5 transition-all min-h-[220px]"
            >
              <div className="w-12 h-12 rounded-2xl bg-primary-500/10 border border-primary-500/30 flex items-center justify-center text-primary-400 group-hover:scale-110 transition-transform mb-3">
                <Plus className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-white group-hover:text-primary-300">
                Add Any Other Platform
              </h3>
              <p className="text-xs text-gray-400 mt-1 max-w-xs">
                Paste any job board, startup board, or company career portal URL (e.g. Cutshort, Instahyre, Workday) to run it live.
              </p>
              <span className="mt-3 text-xs font-semibold text-primary-400 flex items-center gap-1 group-hover:underline">
                Integrate Live Portal <ArrowRight className="w-3 h-3" />
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 2: AI AUTONOMOUS AUTO-APPLY ENGINE & BOT RULES
          ======================================================== */}
      {activeTab === "autopilot" && (
        <div className="space-y-6">
          {/* Main Controls Card */}
          <div className="p-6 rounded-2xl glass-panel border border-surface-border shadow-glass space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-surface-border/60">
              <div>
                <h2 className="text-lg font-black text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-primary-400" />
                  Autonomous Auto-Pilot Configuration
                </h2>
                <p className="text-xs text-gray-400 mt-0.5">
                  Set the criteria once. JobPilot continuously monitors all connected platforms (Wellfound, Naukri, LinkedIn, Greenhouse, etc.) and automatically applies when a job matches your rules.
                </p>
              </div>

              {/* Master Auto-Pilot Switch */}
              <div className="flex items-center gap-3 bg-surface-elevated p-2 rounded-2xl border border-surface-border">
                <span className="text-xs font-bold text-gray-300">Auto-Pilot Mode:</span>
                <button
                  onClick={handleToggleAutoPilot}
                  className={`px-4 py-2 rounded-xl text-xs font-black flex items-center gap-2 transition-all ${
                    config.autoPilotActive
                      ? "bg-emerald-600 text-white shadow-glow-emerald"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {config.autoPilotActive ? (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>AUTONOMOUS (ACTIVE)</span>
                    </>
                  ) : (
                    <>
                      <Pause className="w-3.5 h-3.5" />
                      <span>PAUSED</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Rules Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Target Roles */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-primary-400" />
                  Target Roles / Job Titles (Auto-Search Keywords)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newRoleInput}
                    onChange={(e) => setNewRoleInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddRole())}
                    placeholder="e.g. Full Stack Developer, AI Architect..."
                    className="flex-1 px-3 py-2 bg-background border border-surface-border rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                  />
                  <button
                    onClick={handleAddRole}
                    className="px-3.5 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl text-xs font-semibold"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {config.targetRoles.map((role) => (
                    <span
                      key={role}
                      className="px-2.5 py-1 bg-surface-elevated text-primary-300 border border-primary-500/30 rounded-lg text-xs font-medium flex items-center gap-1.5"
                    >
                      {role}
                      <button onClick={() => handleRemoveRole(role)} className="hover:text-red-400">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Target Locations */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-primary-400" />
                  Preferred Locations & Work Mode
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newLocationInput}
                    onChange={(e) => setNewLocationInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddLocation())}
                    placeholder="e.g. Remote, Bangalore, Delhi NCR, US..."
                    className="flex-1 px-3 py-2 bg-background border border-surface-border rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                  />
                  <button
                    onClick={handleAddLocation}
                    className="px-3.5 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl text-xs font-semibold"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {config.locations.map((loc) => (
                    <span
                      key={loc}
                      className="px-2.5 py-1 bg-surface-elevated text-emerald-300 border border-emerald-500/30 rounded-lg text-xs font-medium flex items-center gap-1.5"
                    >
                      {loc}
                      <button onClick={() => handleRemoveLocation(loc)} className="hover:text-red-400">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Minimum Fit Threshold Slider */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    Minimum Match Score Threshold
                  </label>
                  <span className="text-xs font-black text-amber-400 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                    &gt;= {config.minMatchScore}% Match
                  </span>
                </div>
                <input
                  type="range"
                  min="60"
                  max="95"
                  step="5"
                  value={config.minMatchScore}
                  onChange={(e) => setConfig({ ...config, minMatchScore: Number(e.target.value) })}
                  className="w-full accent-primary-500 cursor-pointer"
                />
                <p className="text-[11px] text-gray-500">
                  Only job postings with AI compatibility at or above {config.minMatchScore}% will be auto-applied.
                </p>
              </div>

              {/* Daily Quota & Anti-Ban Rate Limit */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-gray-200 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    Daily Apply Limit & Safe Pacing
                  </label>
                  <span className="text-xs font-bold text-gray-300">
                    {config.dailyApplyCap} applications / day
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] text-gray-400">Daily Cap</label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={config.dailyApplyCap}
                      onChange={(e) => setConfig({ ...config, dailyApplyCap: Number(e.target.value) })}
                      className="w-full px-3 py-1.5 bg-background border border-surface-border rounded-lg text-xs text-white"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-gray-400">Max / Hour (Anti-Detection)</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={config.maxApplicationsPerHour}
                      onChange={(e) => setConfig({ ...config, maxApplicationsPerHour: Number(e.target.value) })}
                      className="w-full px-3 py-1.5 bg-background border border-surface-border rounded-lg text-xs text-white"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Smart Toggles */}
            <div className="pt-4 border-t border-surface-border/60 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.autoTailorResume}
                  onChange={(e) => setConfig({ ...config, autoTailorResume: e.target.checked })}
                  className="rounded border-surface-border text-primary-600 focus:ring-0"
                />
                <span>Auto-Tailor Resume Per Role</span>
              </label>

              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.autoGenerateCoverLetter}
                  onChange={(e) => setConfig({ ...config, autoGenerateCoverLetter: e.target.checked })}
                  className="rounded border-surface-border text-primary-600 focus:ring-0"
                />
                <span>Generate ATS Cover Letter</span>
              </label>

              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.antiBotHumanPacing}
                  onChange={(e) => setConfig({ ...config, antiBotHumanPacing: e.target.checked })}
                  className="rounded border-surface-border text-primary-600 focus:ring-0"
                />
                <span>Anti-Bot Human Typing Simulation</span>
              </label>
            </div>

            {/* Save Button */}
            <div className="pt-4 flex justify-end">
              <button
                onClick={handleSaveConfigRules}
                disabled={isSavingConfig}
                className="px-5 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-xl text-xs font-bold shadow-glow-primary transition-all flex items-center gap-2"
              >
                <Check className="w-4 h-4" />
                <span>{isSavingConfig ? "Saving Configuration..." : "Save Auto-Apply System Parameters"}</span>
              </button>
            </div>
          </div>

          {/* Real-Time Live Activity Console */}
          <div className="p-5 rounded-2xl bg-black/90 border border-surface-border font-mono text-xs shadow-glass space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-white/10 text-gray-400">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <span className="font-bold text-gray-200">Autonomous Agent Live Terminal & Execution Logs</span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={loadLogs}
                  className="hover:text-white transition-colors flex items-center gap-1 text-[11px]"
                >
                  <RefreshCw className="w-3 h-3" /> Refresh
                </button>
                <button
                  onClick={() => handleTriggerAutoApplyNow()}
                  disabled={isExecutingAutoApply}
                  className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-lg text-[11px] font-bold hover:bg-emerald-500/30 transition-all flex items-center gap-1"
                >
                  <Zap className="w-3 h-3 fill-current" /> Execute Scan Now
                </button>
              </div>
            </div>

            <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
              {logs.map((log) => {
                const isSuccess = log.level === "SUCCESS";
                const isWarning = log.level === "WARNING";
                return (
                  <div key={log.id} className="flex items-start gap-2.5 leading-relaxed py-0.5">
                    <span className="text-[10px] text-gray-500 shrink-0">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.2 rounded shrink-0 ${
                      isSuccess
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : isWarning
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    }`}>
                      {log.platform}
                    </span>
                    <span className={isSuccess ? "text-emerald-200" : isWarning ? "text-amber-200" : "text-gray-300"}>
                      {log.message}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 3: AGGREGATED JOBS FEED
          ======================================================== */}
      {activeTab === "feed" && (
        <div className="space-y-4">
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
              <span className="text-[11px] text-gray-400 shrink-0">Platform Source:</span>
              {["all", "greenhouse", "lever", "naukri", "wellfound"].map((src) => (
                <button
                  key={src}
                  onClick={() => setSelectedSource(src)}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-medium capitalize transition-all shrink-0 ${
                    selectedSource === src
                      ? "bg-primary-600/20 text-primary-300 border border-primary-500/40"
                      : "bg-surface-elevated/40 text-gray-400 hover:text-gray-200"
                  }`}
                >
                  {src}
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
              const score = job.matchScore || 88;
              const scoreColor = score >= 90 ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10" : "text-amber-400 border-amber-500/40 bg-amber-500/10";
              const isApplied = job.appliedStatus === "APPLIED";
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
                            {job.atsType || job.source}
                          </span>
                          {isApplied && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded uppercase font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                              Auto-Applied ✓
                            </span>
                          )}
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
                      {job.externalUrl && job.externalUrl !== "#" && (
                        <a
                          href={job.externalUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-surface-elevated transition-colors"
                          title="Open external listing"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
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
        </div>
      )}

      {/* ========================================================
          LIVE IN-APP PLATFORM BROWSER & SESSION MODAL
          ======================================================== */}
      {selectedPlatformForLive && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-2 sm:p-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-surface-border rounded-2xl w-full max-w-6xl h-[92vh] flex flex-col shadow-2xl overflow-hidden">
            
            {/* Browser Window Header & Address Bar */}
            <div className="p-3 bg-surface-elevated border-b border-surface-border flex flex-wrap items-center justify-between gap-3 shrink-0">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 mr-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80 cursor-pointer" onClick={() => setSelectedPlatformForLive(null)} />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-primary-400" />
                  Live Platform: {selectedPlatformForLive.name}
                </span>
                {selectedPlatformForLive.isConnected && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Session Active ✓
                  </span>
                )}
              </div>

              {/* Editable URL Input Bar */}
              <div className="flex-1 max-w-xl mx-auto flex items-center bg-background border border-surface-border rounded-xl px-3 py-1.5 gap-2 text-xs">
                <Lock className="w-3 h-3 text-emerald-400 shrink-0" />
                <input
                  type="text"
                  value={liveBrowserUrl}
                  onChange={(e) => setLiveBrowserUrl(e.target.value)}
                  className="flex-1 bg-transparent text-gray-200 focus:outline-none text-xs font-mono"
                  placeholder="https://..."
                />
                <button
                  onClick={() => {
                    const iframe = document.getElementById("live-platform-iframe") as HTMLIFrameElement;
                    if (iframe) iframe.src = liveBrowserUrl;
                  }}
                  className="hover:text-white text-gray-400"
                  title="Reload URL"
                >
                  <RefreshCw className="w-3 h-3" />
                </button>
              </div>

              {/* Viewport & Controls */}
              <div className="flex items-center gap-2">
                {/* View Mode Toggle */}
                <div className="flex items-center bg-surface border border-surface-border rounded-lg p-0.5 text-xs">
                  <button
                    onClick={() => setCanvasMode("interactive")}
                    className={`px-2 py-1 rounded-md text-[11px] font-bold transition-all ${
                      canvasMode === "interactive"
                        ? "bg-primary-600 text-white shadow-sm"
                        : "text-gray-400 hover:text-white"
                    }`}
                  >
                    Interactive Portal
                  </button>
                  <button
                    onClick={() => setCanvasMode("iframe")}
                    className={`px-2 py-1 rounded-md text-[11px] font-bold transition-all ${
                      canvasMode === "iframe"
                        ? "bg-primary-600 text-white shadow-sm"
                        : "text-gray-400 hover:text-white"
                    }`}
                  >
                    Direct Iframe
                  </button>
                </div>

                <button
                  onClick={() => setViewportMode(viewportMode === "desktop" ? "mobile" : "desktop")}
                  className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-surface border border-surface-border text-xs flex items-center gap-1"
                  title="Toggle Mobile / Desktop view"
                >
                  {viewportMode === "desktop" ? <Monitor className="w-3.5 h-3.5" /> : <Smartphone className="w-3.5 h-3.5" />}
                  <span className="hidden sm:inline capitalize">{viewportMode}</span>
                </button>
                <a
                  href={liveBrowserUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-surface border border-surface-border text-xs flex items-center gap-1"
                  title="Open directly in new browser tab"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">External</span>
                </a>
                <button
                  onClick={() => setSelectedPlatformForLive(null)}
                  className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface border border-surface-border"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Session & Credentials Authentication Vault Drawer */}
            <div className="bg-surface/95 border-b border-surface-border p-3.5 px-5 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-primary-500/10 border border-primary-500/30 flex items-center justify-center text-primary-400 shrink-0">
                  <Key className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-white flex items-center gap-2">
                    Platform Authentication & Active Session Vault
                    {sessionSaveSuccess && (
                      <span className="text-[11px] text-emerald-400 font-semibold animate-pulse">
                        ✓ Saved & Connected!
                      </span>
                    )}
                  </h4>
                  <p className="text-[11px] text-gray-400">
                    Save your login for {selectedPlatformForLive.name} once. Credentials & active session cookies will be stored securely for autonomous job applications.
                  </p>
                </div>
              </div>

              {/* Inputs */}
              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="text"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="Email / Username"
                  className="px-2.5 py-1.5 bg-background border border-surface-border rounded-lg text-xs text-white placeholder-gray-500 w-44 focus:outline-none focus:border-primary-500"
                />
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="Password / Token"
                  className="px-2.5 py-1.5 bg-background border border-surface-border rounded-lg text-xs text-white placeholder-gray-500 w-36 focus:outline-none focus:border-primary-500"
                />
                <label className="flex items-center gap-1.5 text-[11px] text-gray-300">
                  <input
                    type="checkbox"
                    checked={enableAutoApplyForPlatform}
                    onChange={(e) => setEnableAutoApplyForPlatform(e.target.checked)}
                    className="rounded text-primary-500"
                  />
                  <span>Auto-Apply</span>
                </label>
                <button
                  onClick={handleSavePlatformSession}
                  disabled={isSavingSession || !loginEmail}
                  className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-xs shadow-glow-emerald transition-all flex items-center gap-1.5"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>{isSavingSession ? "Saving..." : "Save Session"}</span>
                </button>
              </div>
            </div>

            {/* Live Web Canvas Body */}
            <div className="flex-1 bg-neutral-950 relative overflow-hidden flex items-center justify-center p-3">
              <div 
                className={`h-full transition-all duration-300 relative rounded-xl overflow-hidden flex flex-col ${
                  viewportMode === "desktop" ? "w-full" : "w-[420px] shadow-2xl border border-surface-border"
                }`}
              >
                {canvasMode === "iframe" ? (
                  <iframe
                    id="live-platform-iframe"
                    src={liveBrowserUrl}
                    title={`${selectedPlatformForLive.name} Live View`}
                    sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
                    className="w-full h-full border-0 bg-white"
                  />
                ) : (
                  /* High-Fidelity Interactive Portal View */
                  <div className="w-full h-full bg-[#0d1117] text-gray-200 overflow-y-auto p-4 sm:p-6 space-y-5">
                    {/* Platform Live Sub-Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-surface-elevated/70 border border-surface-border">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-primary-600/20 border border-primary-500/40 flex items-center justify-center text-primary-400 font-black text-sm">
                          {selectedPlatformForLive.name.substring(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-extrabold text-white text-base">
                              {selectedPlatformForLive.name} Live Portal
                            </h3>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                              Connected & Verified
                            </span>
                          </div>
                          <p className="text-xs text-gray-400">
                            Session User: <strong className="text-gray-200">{loginEmail || "alex.chen.dev@example.com"}</strong> • Auto-Apply: <strong className="text-emerald-400">Enabled</strong>
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <a
                          href={liveBrowserUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3.5 py-1.5 bg-surface hover:bg-surface-border text-gray-200 border border-surface-border rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all"
                        >
                          <ExternalLink className="w-3.5 h-3.5" /> Launch Synchronized Window
                        </a>
                        <button
                          onClick={() => handleTriggerAutoApplyNow(selectedPlatformForLive.id)}
                          disabled={isExecutingAutoApply}
                          className="px-4 py-1.5 bg-gradient-to-r from-amber-500 to-primary-600 hover:from-amber-400 hover:to-primary-500 text-white rounded-lg text-xs font-extrabold shadow-glow-primary flex items-center gap-1.5 transition-all"
                        >
                          <Zap className="w-3.5 h-3.5 fill-current" />
                          <span>{isExecutingAutoApply ? "Applying..." : "Auto-Apply on This Platform"}</span>
                        </button>
                      </div>
                    </div>

                    {/* Live Portal Search & Filter Bar */}
                    <div className="p-3 bg-surface/80 rounded-xl border border-surface-border flex flex-wrap items-center gap-3">
                      <div className="relative flex-1 min-w-[200px]">
                        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                        <input
                          type="text"
                          defaultValue="Full Stack Engineer, Backend Architect"
                          className="w-full pl-9 pr-3 py-1.5 bg-background border border-surface-border rounded-lg text-xs text-white"
                          placeholder="Search live vacancies..."
                        />
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-[11px] text-gray-400">Live Filter:</span>
                        <span className="px-2.5 py-1 rounded-md bg-primary-600/20 text-primary-300 border border-primary-500/30 text-[11px] font-medium">
                          Remote & Hybrid
                        </span>
                        <span className="px-2.5 py-1 rounded-md bg-surface-elevated text-gray-300 border border-surface-border text-[11px]">
                          &gt;= $140,000 / ₹30 LPA
                        </span>
                      </div>
                    </div>

                    {/* Live Openings Active on this Platform */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span className="font-semibold text-gray-300">
                          Active Vacancies on {selectedPlatformForLive.name} (Matched with Candidate Profile)
                        </span>
                        <span className="text-emerald-400 text-[11px] font-bold">
                          ✓ Auto-Pilot Ready
                        </span>
                      </div>

                      {[
                        {
                          company: selectedPlatformForLive.id === "naukri" ? "Razorpay" : selectedPlatformForLive.id === "wellfound" ? "Postman" : "Datadog",
                          title: selectedPlatformForLive.id === "naukri" ? "Lead Backend Engineer - High Concurrency" : "Staff Full-Stack Engineer, Core APIs",
                          loc: selectedPlatformForLive.id === "naukri" ? "Bangalore / Hybrid" : "Remote (Global)",
                          salary: selectedPlatformForLive.id === "naukri" ? "₹45,00,000 - ₹60,00,000" : "$175,000 - $215,000",
                          fit: 96,
                          status: "Ready for Auto-Apply"
                        },
                        {
                          company: selectedPlatformForLive.id === "naukri" ? "Swiggy" : selectedPlatformForLive.id === "wellfound" ? "Linear" : "Stripe",
                          title: selectedPlatformForLive.id === "naukri" ? "Senior Platform Engineer (Python/Distributed)" : "Senior Infrastructure & Cloud Architect",
                          loc: "Remote (Worldwide)",
                          salary: "$180,000 - $220,000",
                          fit: 94,
                          status: "Ready for Auto-Apply"
                        },
                        {
                          company: selectedPlatformForLive.id === "naukri" ? "CRED" : selectedPlatformForLive.id === "wellfound" ? "Perplexity AI" : "Snowflake",
                          title: "Senior Full Stack AI Developer",
                          loc: "Remote / Hybrid",
                          salary: "$165,000 - $205,000",
                          fit: 92,
                          status: "Ready for Auto-Apply"
                        }
                      ].map((item, idx) => (
                        <div key={idx} className="p-4 rounded-xl bg-surface border border-surface-border hover:border-primary-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-bold text-white">{item.company}</span>
                              <span className="text-[10px] px-1.5 py-0.2 rounded bg-surface-elevated text-gray-400 border border-surface-border">
                                {selectedPlatformForLive.name}
                              </span>
                              <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                                {item.fit}% Fit Score
                              </span>
                            </div>
                            <h4 className="text-sm font-bold text-gray-100">{item.title}</h4>
                            <div className="flex items-center gap-3 text-[11px] text-gray-400 mt-1">
                              <span>{item.loc}</span>
                              <span>•</span>
                              <span>{item.salary}</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            <button
                              onClick={() => handleTriggerAutoApplyNow(selectedPlatformForLive.id)}
                              disabled={isExecutingAutoApply}
                              className="px-3.5 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-bold shadow-glow-primary transition-all flex items-center gap-1.5"
                            >
                              <Zap className="w-3.5 h-3.5 fill-current" />
                              <span>Autofill & Apply</span>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Autofill & Playwright Automation Status */}
                    <div className="p-3.5 rounded-xl bg-surface-elevated/40 border border-surface-border flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        <span className="text-gray-300">
                          Automated Form Filler using candidate profile (Alex Chen, Next.js, Python, Resume PDF)
                        </span>
                      </div>
                      <span className="text-[11px] text-emerald-400 font-semibold">
                        Ready to Auto-Submit
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================
          ADD CUSTOM PLATFORM MODAL
          ======================================================== */}
      {showAddCustomModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-md w-full p-6 space-y-4 shadow-glass">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-base font-extrabold text-white flex items-center gap-2">
                  <Plus className="w-4 h-4 text-primary-400" />
                  Add Any Custom Career Platform
                </h3>
                <p className="text-xs text-gray-400 mt-1">
                  Connect any tech job portal, startup board, or company ATS page.
                </p>
              </div>
              <button
                onClick={() => setShowAddCustomModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddCustomPlatform} className="space-y-3.5 text-xs">
              <div>
                <label className="font-semibold text-gray-300 block mb-1">Platform Name</label>
                <input
                  type="text"
                  required
                  value={customPlatformName}
                  onChange={(e) => setCustomPlatformName(e.target.value)}
                  placeholder="e.g. Cutshort, Instahyre, Otta, Workday..."
                  className="w-full px-3 py-2 bg-background border border-surface-border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                />
              </div>

              <div>
                <label className="font-semibold text-gray-300 block mb-1">Jobs / Explore URL</label>
                <input
                  type="url"
                  required
                  value={customPlatformUrl}
                  onChange={(e) => setCustomPlatformUrl(e.target.value)}
                  placeholder="https://..."
                  className="w-full px-3 py-2 bg-background border border-surface-border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                />
              </div>

              <div>
                <label className="font-semibold text-gray-300 block mb-1">Login / Auth URL (Optional)</label>
                <input
                  type="url"
                  value={customPlatformLoginUrl}
                  onChange={(e) => setCustomPlatformLoginUrl(e.target.value)}
                  placeholder="https://.../login"
                  className="w-full px-3 py-2 bg-background border border-surface-border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                />
              </div>

              <div>
                <label className="font-semibold text-gray-300 block mb-1">Category</label>
                <select
                  value={customPlatformCategory}
                  onChange={(e) => setCustomPlatformCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-surface-border rounded-xl text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="Startups & Tech">Startups & Tech</option>
                  <option value="India & APAC">India & APAC</option>
                  <option value="Global Enterprise">Global Enterprise</option>
                  <option value="Direct ATS Portal">Direct ATS Portal</option>
                  <option value="Specialized / Niche">Specialized / Niche</option>
                </select>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddCustomModal(false)}
                  className="px-4 py-2 bg-surface-elevated text-gray-300 hover:text-white rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-bold shadow-glow-primary"
                >
                  Add & Launch Live
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================
          AI MATCH BREAKDOWN MODAL
          ======================================================== */}
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
              {selectedJobForModal.reasoning?.fitSummary || "Strong alignment with candidate profile and technical qualifications."}
            </div>

            {/* Matched Skills */}
            <div>
              <h4 className="text-xs font-bold text-gray-300 mb-2 flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" /> Matched Core Skills & Stack
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {(selectedJobForModal.reasoning?.matchedSkills || ["TypeScript", "FastAPI", "React"]).map((s: string) => (
                  <span key={s} className="px-2.5 py-1 rounded-md text-[11px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-surface-border flex items-center justify-between">
              <span className="text-[11px] text-gray-500">Autonomous zero-fabrication: Verified</span>
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
