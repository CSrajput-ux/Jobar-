"use client";

import React, { useState } from "react";
import { 
  Sliders, 
  User, 
  Upload, 
  Save, 
  ShieldCheck, 
  Power, 
  Check, 
  Lock, 
  DollarSign, 
  Globe, 
  CheckCircle2,
  FileCheck
} from "lucide-react";

interface SettingsViewProps {
  killSwitchActive: boolean;
  onToggleKillSwitch: (active: boolean) => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  killSwitchActive,
  onToggleKillSwitch
}) => {
  const [activeTab, setActiveTab] = useState<"preferences" | "profile" | "qa" | "security">("preferences");
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Preferences State
  const [targetRoles, setTargetRoles] = useState("Staff Software Engineer, Senior Full Stack Engineer, Principal Backend Engineer");
  const [minSalary, setMinSalary] = useState(175000);
  const [applyMode, setApplyMode] = useState<"MANUAL" | "APPROVAL_QUEUE" | "FULL_AUTO">("APPROVAL_QUEUE");
  const [dailyCap, setDailyCap] = useState(15);
  const [minMatchScore, setMinMatchScore] = useState(75);
  const [visaSponsorship, setVisaSponsorship] = useState(false);

  // Common QA State
  const [noticePeriod, setNoticePeriod] = useState(14);
  const [workAuth, setWorkAuth] = useState("Authorized to work in US without sponsorship");
  const [whyCompany, setWhyCompany] = useState("Excited by the mission, high-caliber engineering culture, and developer platform challenges.");

  const handleSave = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Sliders className="w-5 h-5 text-primary-400" />
            Candidate Settings & Preferences
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Configure automation modes, ATS answer vaults, salary requirements, and security governance.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary flex items-center gap-1.5 transition-all"
        >
          {saveSuccess ? <Check className="w-4 h-4 text-emerald-300" /> : <Save className="w-4 h-4" />}
          <span>{saveSuccess ? "Preferences Saved!" : "Save Changes"}</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-surface-border gap-6">
        {[
          { id: "preferences", label: "Job & Auto-Apply Preferences" },
          { id: "qa", label: "Reusable Application QA Vault" },
          { id: "profile", label: "Master CV & Parsing" },
          { id: "security", label: "Security & Governance" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`pb-3 text-xs font-bold transition-all relative ${
              activeTab === tab.id ? "text-primary-400" : "text-gray-400 hover:text-gray-200"
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"></div>
            )}
          </button>
        ))}
      </div>

      {/* Tab: Preferences */}
      {activeTab === "preferences" && (
        <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-6">
          {/* Apply Mode Selector */}
          <div>
            <label className="text-xs font-bold text-gray-200 block mb-2">Automation Application Mode</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { id: "MANUAL", title: "Manual Review Only", desc: "AI highlights jobs and tailors resumes; you apply manually." },
                { id: "APPROVAL_QUEUE", title: "Approval Queue (Default)", desc: "AI prepares submission and awaits your 1-click approval." },
                { id: "FULL_AUTO", title: "Full Autonomous", desc: "Applies automatically for matches above threshold within daily cap." }
              ].map((m) => (
                <div
                  key={m.id}
                  onClick={() => setApplyMode(m.id as any)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    applyMode === m.id
                      ? "bg-primary-950/40 border-primary-500 shadow-sm"
                      : "bg-surface border-surface-border hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white">{m.title}</span>
                    {applyMode === m.id && <CheckCircle2 className="w-4 h-4 text-primary-400" />}
                  </div>
                  <p className="text-[11px] text-gray-400 leading-relaxed">{m.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-300">Target Roles (Comma-separated)</label>
              <input
                type="text"
                value={targetRoles}
                onChange={(e) => setTargetRoles(e.target.value)}
                className="w-full px-3.5 py-2 bg-surface/80 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-300 flex items-center justify-between">
                <span>Minimum Salary Expectation:</span>
                <span className="text-emerald-400 font-extrabold">${minSalary.toLocaleString()} USD/yr</span>
              </label>
              <input
                type="range"
                min="100000"
                max="250000"
                step="5000"
                value={minSalary}
                onChange={(e) => setMinSalary(Number(e.target.value))}
                className="w-full accent-primary-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-300">Daily Apply Cap</label>
              <input
                type="number"
                value={dailyCap}
                onChange={(e) => setDailyCap(Number(e.target.value))}
                className="w-full px-3.5 py-2 bg-surface/80 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-300">Min Match Score Threshold</label>
              <input
                type="number"
                value={minMatchScore}
                onChange={(e) => setMinMatchScore(Number(e.target.value))}
                className="w-full px-3.5 py-2 bg-surface/80 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500"
              />
            </div>

            <div className="space-y-1.5 flex flex-col justify-end">
              <label className="flex items-center gap-2 cursor-pointer pb-2">
                <input
                  type="checkbox"
                  checked={visaSponsorship}
                  onChange={(e) => setVisaSponsorship(e.target.checked)}
                  className="rounded bg-surface border-surface-border text-primary-600 focus:ring-0"
                />
                <span className="text-xs text-gray-300 font-medium">Require Visa Sponsorship</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Tab: QA Vault */}
      {activeTab === "qa" && (
        <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-4">
          <p className="text-xs text-gray-400">
            Pre-saved answers for ATS forms (Greenhouse, Lever, Ashby). The Playwright engine auto-populates these during submission.
          </p>

          <div className="space-y-3">
            <div className="space-y-1">
              <label className="text-xs font-bold text-gray-300">Notice Period (Days)</label>
              <input
                type="number"
                value={noticePeriod}
                onChange={(e) => setNoticePeriod(Number(e.target.value))}
                className="w-full px-3.5 py-2 bg-surface/80 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-gray-300">Work Authorization Status</label>
              <input
                type="text"
                value={workAuth}
                onChange={(e) => setWorkAuth(e.target.value)}
                className="w-full px-3.5 py-2 bg-surface/80 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-gray-300">Default "Why This Company?" Statement</label>
              <textarea
                rows={3}
                value={whyCompany}
                onChange={(e) => setWhyCompany(e.target.value)}
                className="w-full p-3.5 bg-surface/80 border border-surface-border rounded-lg text-xs text-white focus:outline-none focus:border-primary-500 font-sans"
              />
            </div>
          </div>
        </div>
      )}

      {/* Tab: Security & Governance */}
      {activeTab === "security" && (
        <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-6">
          <div className="flex items-start justify-between pb-4 border-b border-surface-border">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Power className="w-4 h-4 text-rose-400" />
                Emergency Automation Kill Switch
              </h3>
              <p className="text-xs text-gray-400 mt-1 max-w-xl">
                Immediately halts all active Celery workers, cancels pending Playwright form submissions, and freezes outbound email dispatch.
              </p>
            </div>
            <button
              onClick={() => onToggleKillSwitch(!killSwitchActive)}
              className={`px-4 py-2 rounded-lg text-xs font-bold border transition-all ${
                killSwitchActive
                  ? "bg-rose-500/20 text-rose-300 border-rose-500/50 hover:bg-rose-500/30"
                  : "bg-surface-elevated text-gray-300 border-surface-border hover:border-gray-500"
              }`}
            >
              {killSwitchActive ? "RESUME AUTOMATION" : "ENGAGE KILL SWITCH"}
            </button>
          </div>

          <div className="space-y-3 text-xs">
            <h4 className="font-bold text-gray-200">Compliance & Encryption Status:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3.5 rounded-xl bg-surface border border-surface-border">
                <div className="flex items-center gap-2 text-emerald-400 font-bold mb-1">
                  <ShieldCheck className="w-4 h-4" />
                  AES-256-GCM Authenticated Encryption
                </div>
                <p className="text-[11px] text-gray-400">
                  Google OAuth tokens (Gmail & Calendar) and candidate PII are encrypted at rest with unique 96-bit IVs.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-surface border border-surface-border">
                <div className="flex items-center gap-2 text-emerald-400 font-bold mb-1">
                  <FileCheck className="w-4 h-4" />
                  Zero-Fabrication Guardrail
                </div>
                <p className="text-[11px] text-gray-400">
                  AST schema validator cross-checks generated resume bullets against candidate master experience ground truth.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Master CV Upload */}
      {activeTab === "profile" && (
        <div className="p-6 rounded-2xl glass-card border border-surface-border space-y-4">
          <div className="border-2 border-dashed border-surface-border hover:border-primary-500/50 rounded-2xl p-8 text-center transition-all cursor-pointer bg-surface/40">
            <Upload className="w-8 h-8 text-primary-400 mx-auto mb-2" />
            <div className="text-xs font-bold text-white">Upload New CV (PDF / DOCX)</div>
            <div className="text-[11px] text-gray-500 mt-0.5">
              Claude 3.5 Sonnet extracts experience highlights, technical skills, and education into normalized JSON.
            </div>
          </div>

          <div className="p-4 rounded-xl bg-surface border border-surface-border text-xs text-gray-300">
            <span className="font-bold text-white block mb-1">Active Parsed Profile:</span>
            Alex Chen • Staff Full-Stack & Distributed Systems Engineer • 8+ years experience • Python, TypeScript, Next.js, pgvector, Redis, Docker
          </div>
        </div>
      )}
    </div>
  );
};
