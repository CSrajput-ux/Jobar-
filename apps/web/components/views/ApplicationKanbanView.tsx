"use client";

import React, { useState } from "react";
import { 
  Layers, 
  ExternalLink, 
  Image as ImageIcon, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  X,
  FileText,
  Building,
  MoreVertical
} from "lucide-react";

interface ApplicationKanbanViewProps {
  onApprove: (appId: string) => void;
  onOpenTailoring: (job: any) => void;
}

export const ApplicationKanbanView: React.FC<ApplicationKanbanViewProps> = ({
  onApprove,
  onOpenTailoring
}) => {
  const [proofModalUrl, setProofModalUrl] = useState<string | null>(null);

  const [applications, setApplications] = useState([
    {
      id: "10000000-0000-0000-0000-000000000003",
      companyName: "Linear",
      title: "Staff Infrastructure & Systems Engineer",
      status: "SAVED",
      atsType: "lever",
      appliedAt: null,
      proofScreenshotUrl: null,
      notes: "High relevance to real-time sync systems.",
      salary: "$180,000 - $220,000"
    },
    {
      id: "10000000-0000-0000-0000-000000000001",
      companyName: "Vercel",
      title: "Senior Full-Stack Engineer, AI Platforms",
      status: "QUEUED_FOR_APPROVAL",
      atsType: "greenhouse",
      appliedAt: null,
      proofScreenshotUrl: null,
      notes: "96% match. Tailored resume & cover letter prepared.",
      salary: "$170,000 - $210,000"
    },
    {
      id: "10000000-0000-0000-0000-000000000002",
      companyName: "Supabase",
      title: "Backend Engineer, Postgres & Vector Engine",
      status: "APPLIED",
      atsType: "greenhouse",
      appliedAt: "2026-09-28T14:22:00Z",
      proofScreenshotUrl: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
      notes: "Submitted via Greenhouse automation. Confirmation verified.",
      salary: "$165,000 - $205,000"
    },
    {
      id: "10000000-0000-0000-0000-000000000004",
      companyName: "Supabase",
      title: "Backend Engineer, Postgres & Vector Engine",
      status: "INTERVIEW",
      atsType: "greenhouse",
      appliedAt: "2026-09-28T14:22:00Z",
      proofScreenshotUrl: null,
      notes: "Technical screen scheduled for this Friday 11am PT.",
      salary: "$165,000 - $205,000"
    }
  ]);

  const stages = [
    { id: "SAVED", title: "Saved", count: applications.filter(a => a.status === "SAVED").length, border: "border-gray-500/30" },
    { id: "QUEUED_FOR_APPROVAL", title: "Approval Queue", count: applications.filter(a => a.status === "QUEUED_FOR_APPROVAL").length, border: "border-amber-500/40" },
    { id: "APPLIED", title: "Applied", count: applications.filter(a => a.status === "APPLIED").length, border: "border-indigo-500/40" },
    { id: "INTERVIEW", title: "Interviews", count: applications.filter(a => a.status === "INTERVIEW").length, border: "border-emerald-500/40" },
    { id: "OFFER", title: "Offers", count: applications.filter(a => a.status === "OFFER").length, border: "border-purple-500/40" },
    { id: "REJECTED", title: "Archived", count: applications.filter(a => a.status === "REJECTED").length, border: "border-zinc-500/30" },
  ];

  const handleMoveStage = (appId: string, newStage: string) => {
    setApplications(prev => prev.map(a => a.id === appId ? { ...a, status: newStage } : a));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary-400" />
            Application Pipeline Kanban
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real-time stage tracking with Playwright automated proofs and audit trails.
          </p>
        </div>
      </div>

      {/* Kanban Board Horizontal Scroll */}
      <div className="flex gap-4 overflow-x-auto pb-4 items-start min-h-[600px]">
        {stages.map((col) => {
          const colApps = applications.filter(a => a.status === col.id);
          return (
            <div
              key={col.id}
              className={`w-72 shrink-0 rounded-xl bg-surface/70 border ${col.border} p-3 flex flex-col gap-3 min-h-[480px]`}
            >
              {/* Column Header */}
              <div className="flex items-center justify-between px-1 py-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-gray-200">{col.title}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-surface-elevated text-gray-400 border border-surface-border">
                    {col.count}
                  </span>
                </div>
              </div>

              {/* Cards list */}
              <div className="space-y-3 flex-1">
                {colApps.map((app) => (
                  <div
                    key={app.id}
                    className="p-3.5 rounded-xl glass-card border border-surface-border hover:border-primary-500/40 transition-all text-xs space-y-2.5 shadow-sm"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="font-bold text-gray-300 text-[11px] block">{app.companyName}</span>
                        <h4 className="font-semibold text-white text-xs mt-0.5 leading-snug">{app.title}</h4>
                      </div>
                      <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-surface-elevated text-gray-400 border border-surface-border shrink-0">
                        {app.atsType}
                      </span>
                    </div>

                    <div className="text-[11px] text-gray-400">
                      {app.salary}
                    </div>

                    {app.notes && (
                      <p className="text-[11px] text-gray-400 bg-surface-elevated/40 p-2 rounded-lg border border-surface-border/50">
                        {app.notes}
                      </p>
                    )}

                    {/* Card Actions */}
                    <div className="pt-2 border-t border-surface-border flex items-center justify-between">
                      {app.status === "QUEUED_FOR_APPROVAL" ? (
                        <button
                          onClick={() => {
                            handleMoveStage(app.id, "APPLIED");
                            onApprove(app.id);
                          }}
                          className="w-full py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-md text-[11px] font-semibold flex items-center justify-center gap-1 shadow-glow-emerald"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" /> 1-Click Approve & Submit
                        </button>
                      ) : app.proofScreenshotUrl ? (
                        <button
                          onClick={() => setProofModalUrl(app.proofScreenshotUrl)}
                          className="text-[11px] text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
                        >
                          <ImageIcon className="w-3.5 h-3.5" /> View Proof Screenshot
                        </button>
                      ) : (
                        <div className="flex items-center justify-between w-full text-[10px] text-gray-500">
                          <span>Stage selector:</span>
                          <select
                            value={app.status}
                            onChange={(e) => handleMoveStage(app.id, e.target.value)}
                            className="bg-surface-elevated border border-surface-border rounded px-1.5 py-0.5 text-gray-300 text-[10px] focus:outline-none"
                          >
                            <option value="SAVED">Saved</option>
                            <option value="QUEUED_FOR_APPROVAL">Queue</option>
                            <option value="APPLIED">Applied</option>
                            <option value="INTERVIEW">Interview</option>
                            <option value="OFFER">Offer</option>
                            <option value="REJECTED">Reject</option>
                          </select>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {colApps.length === 0 && (
                  <div className="h-32 border border-dashed border-surface-border/60 rounded-xl flex items-center justify-center text-xs text-gray-500">
                    No jobs in this stage
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Proof Screenshot Modal */}
      {proofModalUrl && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl max-w-3xl w-full p-6 space-y-4 shadow-glass">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Application Proof of Submission
                </h3>
                <p className="text-xs text-gray-400">Captured automatically by Playwright runner with timestamped payload.</p>
              </div>
              <button
                onClick={() => setProofModalUrl(null)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-elevated"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="relative rounded-xl overflow-hidden border border-surface-border bg-black aspect-video flex items-center justify-center">
              <img
                src={proofModalUrl}
                alt="Submission proof"
                className="object-cover w-full h-full"
              />
              <div className="absolute bottom-3 left-3 bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-surface-border text-[11px] text-gray-200">
                Timestamp: 2026-09-28 14:22:00 UTC • Greenhouse Form Status: 200 OK
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setProofModalUrl(null)}
                className="px-4 py-2 bg-surface-elevated hover:bg-surface-border text-gray-200 rounded-lg text-xs font-semibold"
              >
                Close Proof Viewer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
