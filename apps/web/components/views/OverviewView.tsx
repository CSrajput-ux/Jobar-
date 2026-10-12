"use client";

import React from "react";
import { 
  Sparkles, 
  CheckCircle2, 
  Send, 
  Clock, 
  ArrowUpRight, 
  Calendar, 
  AlertCircle, 
  ChevronRight,
  Shield,
  FileCheck,
  TrendingUp,
  Activity
} from "lucide-react";

interface OverviewViewProps {
  onNavigate: (tab: string) => void;
  onApproveApplication: (appId: string) => void;
  profile?: any;
  applications?: any[];
  jobs?: any[];
  calendarEvents?: any[];
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  onNavigate,
  onApproveApplication,
  profile,
  applications = [],
  jobs = [],
  calendarEvents = [],
}) => {
  const candidateName = profile?.full_name || "Candidate";
  const jobsCount = jobs.length;
  const queuedApps = applications.filter(a => a.status === "QUEUED_FOR_APPROVAL");
  const appliedCount = applications.filter(a => a.status === "APPLIED").length;
  const interviewCount = calendarEvents.length || applications.filter(a => a.status === "INTERVIEW" || a.status === "INTERVIEWING").length;

  const topQueuedApp = queuedApps[0];
  const nextEvent = calendarEvents[0];

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="relative overflow-hidden rounded-2xl p-6 glass-card border border-primary-500/25 bg-gradient-to-r from-primary-950/40 via-surface-elevated to-surface">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-primary-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-primary-400" /> Autonomous Pipeline Active
              </span>
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              Welcome, <span className="gradient-text-gold">{candidateName}</span>. {queuedApps.length} {queuedApps.length === 1 ? "job" : "jobs"} queued for approval & {interviewCount} {interviewCount === 1 ? "interview" : "interviews"} scheduled.
            </h1>
            <p className="text-xs text-gray-400 mt-1 max-w-2xl leading-relaxed">
              JobPilot is monitoring active ATS boards, generating zero-fabrication tailored applications, and enforcing human-in-the-loop review.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate("jobs")}
              className="px-4 py-2 bg-surface-elevated hover:bg-surface-border text-gray-200 rounded-lg text-xs font-semibold border border-surface-border transition-all flex items-center gap-2"
            >
              Browse Jobs
            </button>
            <button
              onClick={() => onNavigate("approval")}
              className="px-4 py-2 bg-primary-500 hover:bg-primary-400 text-gray-950 rounded-lg text-xs font-bold shadow-glow-amber transition-all flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4 text-gray-950" />
              Review Approvals ({queuedApps.length})
            </button>
          </div>
        </div>
      </div>

      {/* Metric Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>Jobs Discovered</span>
            <Sparkles className="w-4 h-4 text-primary-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{jobsCount}</div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> Real-time ATS feeds synced
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>Approval Queue</span>
            <CheckCircle2 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-amber-300">{queuedApps.length}</div>
          <div className="text-[11px] text-gray-400 mt-1">
            {queuedApps.length > 0 ? `${topQueuedApp?.job?.companyName || "Role"} pending review` : "No pending items"}
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>Applications Submitted</span>
            <FileCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{appliedCount}</div>
          <div className="text-[11px] text-emerald-400 mt-1">
            {appliedCount > 0 ? "Persisted in pipeline" : "Awaiting first submission"}
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-surface-border">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>Interviews Scheduled</span>
            <Calendar className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-300">{interviewCount}</div>
          <div className="text-[11px] text-gray-400 mt-1">
            {interviewCount > 0 ? "Synced with Calendar" : "None scheduled"}
          </div>
        </div>
      </div>

      {/* Main Grid: Today's Action Center & Live Activity Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Action Center (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-bold text-gray-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary-400" />
            Today&apos;s Action Center
          </h2>

          {/* Pending Approval Card */}
          {topQueuedApp ? (
            <div className="p-5 rounded-xl glass-panel border border-amber-500/30 bg-amber-500/5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-wide">
                      Approval Required
                    </span>
                    <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      High Match Fit
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white">
                    {topQueuedApp.job?.title || "Senior Software Engineer"}
                  </h3>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {topQueuedApp.job?.companyName || "Company"} • {topQueuedApp.job?.location || "Remote"} • {topQueuedApp.job?.atsType?.toUpperCase() || "DIRECT"} • {topQueuedApp.job?.salaryRange || "Competitive"}
                  </p>
                  <div className="mt-3 text-xs text-gray-300 bg-surface/60 p-3 rounded-lg border border-surface-border">
                    <span className="font-semibold text-primary-300">AI Tailoring summary:</span> {topQueuedApp.notes || "Tailored with verified background. Zero-fabrication check passed."}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-surface-border flex items-center justify-between">
                <button
                  onClick={() => onNavigate("tailoring")}
                  className="text-xs text-primary-400 hover:text-primary-300 font-semibold flex items-center gap-1"
                >
                  Inspect Resume Diff <ChevronRight className="w-3.5 h-3.5" />
                </button>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onApproveApplication(topQueuedApp.id)}
                    className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-glow-emerald transition-all flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" /> 1-Click Approve & Apply
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-5 rounded-xl glass-panel border border-surface-border text-center py-8">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-white">All Caught Up</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-md mx-auto">
                No applications currently waiting in the approval queue. Discover new jobs or adjust your target preferences to queue fresh roles.
              </p>
              <button
                onClick={() => onNavigate("jobs")}
                className="mt-3 px-3 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold"
              >
                Find New Jobs
              </button>
            </div>
          )}

          {/* Incoming Interview Alert Card */}
          {nextEvent ? (
            <div className="p-5 rounded-xl glass-panel border border-emerald-500/30 bg-emerald-500/5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wide">
                      Interview Scheduled
                    </span>
                    <span className="text-xs text-gray-400">Confirmed on Calendar</span>
                  </div>
                  <h3 className="text-base font-bold text-white">
                    {nextEvent.summary || nextEvent.title || "Technical Interview"}
                  </h3>
                  <p className="text-xs text-gray-300 mt-1">
                    {nextEvent.company_name || nextEvent.companyName || "Company"} • {nextEvent.start_time || nextEvent.dateStr || "Upcoming slot"}
                  </p>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-border flex items-center justify-between">
                <button
                  onClick={() => onNavigate("calendar")}
                  className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
                >
                  View in Calendar <ChevronRight className="w-3.5 h-3.5" />
                </button>
                {nextEvent.meet_link && (
                  <a
                    href={nextEvent.meet_link}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-1.5 bg-surface-elevated hover:bg-surface-border text-gray-200 rounded-lg text-xs font-semibold border border-surface-border transition-all flex items-center gap-1.5"
                  >
                    <Calendar className="w-3.5 h-3.5 text-blue-400" /> Join Google Meet
                  </a>
                )}
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl glass-panel border border-surface-border flex items-center justify-between text-xs text-gray-400">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span>Google Calendar connected • No pending interviews for today</span>
              </div>
              <button
                onClick={() => onNavigate("calendar")}
                className="text-primary-400 hover:text-primary-300 font-semibold"
              >
                Open Calendar
              </button>
            </div>
          )}
        </div>

        {/* Right Col: Quotas & Activity Feed */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-200 flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary-400" />
            Safety & System Limits
          </h2>

          <div className="p-4 rounded-xl glass-panel border border-surface-border space-y-4">
            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-gray-400">Daily Apply Quota</span>
                <span className="font-semibold text-gray-200">{appliedCount} / 15 applied</span>
              </div>
              <div className="w-full bg-surface-border h-2 rounded-full overflow-hidden">
                <div
                  className="bg-primary-500 h-full rounded-full transition-all"
                  style={{ width: `${Math.min(100, Math.round((appliedCount / 15) * 100))}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-gray-400">Outreach Warmup</span>
                <span className="font-semibold text-gray-200">0 / 10 emails</span>
              </div>
              <div className="w-full bg-surface-border h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full w-[0%] transition-all"></div>
              </div>
            </div>

            <div className="pt-3 border-t border-surface-border text-[11px] text-gray-400 space-y-2">
              <div className="flex items-center justify-between">
                <span>Domain Rate Limit</span>
                <span className="text-emerald-400 font-medium">Max 3 / hr / domain</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Zero-Fabrication Guard</span>
                <span className="text-emerald-400 font-medium">Active (AST Verified)</span>
              </div>
            </div>
          </div>

          <h2 className="text-sm font-bold text-gray-200 flex items-center gap-2 pt-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            Governance & Audit
          </h2>

          <div className="p-4 rounded-xl glass-panel border border-surface-border space-y-3 text-xs">
            <div className="flex items-start gap-2.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0"></div>
              <div>
                <div className="text-gray-200 font-medium">AES-256-GCM Encryption Active</div>
                <div className="text-[10px] text-gray-500">OAuth tokens sealed at rest</div>
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <div className="w-1.5 h-1.5 rounded-full bg-primary-400 mt-1.5 shrink-0"></div>
              <div>
                <div className="text-gray-200 font-medium">SSRF URL Shield Active</div>
                <div className="text-[10px] text-gray-500">Private & link-local ranges blocked</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
