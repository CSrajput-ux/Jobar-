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
import { api } from "../../lib/api";

interface ApplicationKanbanViewProps {
  onApprove: (appId: string) => void;
  onOpenTailoring: (job: any) => void;
  initialApplications?: any[];
  onRefresh?: () => void;
}

export const ApplicationKanbanView: React.FC<ApplicationKanbanViewProps> = ({
  onApprove,
  onOpenTailoring,
  initialApplications,
  onRefresh,
}) => {
  const [proofModalUrl, setProofModalUrl] = useState<string | null>(null);

  const [applications, setApplications] = useState(() => {
    if (initialApplications !== undefined) {
      return initialApplications.map(a => ({
        id: a.id,
        companyName: a.job?.companyName || "Company",
        title: a.job?.title || "Role",
        status: a.status,
        atsType: a.job?.atsType || "direct",
        appliedAt: a.appliedAt,
        proofScreenshotUrl: a.proofScreenshotUrl,
        notes: a.notes,
        salary: a.job?.salaryRange || "Competitive",
      }));
    }
    return [];
  });

  const stages = [
    { id: "SAVED", title: "Saved", count: applications.filter(a => a.status === "SAVED").length, border: "border-gray-500/30" },
    { id: "QUEUED_FOR_APPROVAL", title: "Approval Queue", count: applications.filter(a => a.status === "QUEUED_FOR_APPROVAL").length, border: "border-amber-500/40" },
    { id: "APPROVED", title: "Approved", count: applications.filter(a => a.status === "APPROVED").length, border: "border-cyan-500/40" },
    { id: "APPLIED", title: "Applied", count: applications.filter(a => a.status === "APPLIED").length, border: "border-indigo-500/40" },
    { id: "INTERVIEW", title: "Interviews", count: applications.filter(a => a.status === "INTERVIEW" || a.status === "INTERVIEWING").length, border: "border-emerald-500/40" },
    { id: "OFFER", title: "Offers", count: applications.filter(a => a.status === "OFFER" || a.status === "OFFERED").length, border: "border-purple-500/40" },
    { id: "REJECTED", title: "Archived", count: applications.filter(a => a.status === "REJECTED" || a.status === "WITHDRAWN").length, border: "border-zinc-500/30" },
  ];

  const handleMoveStage = async (appId: string, newStage: string) => {
    setApplications(prev => prev.map(a => a.id === appId ? { ...a, status: newStage } : a));
    try {
      await api.updateApplicationStage(appId, newStage);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.warn("Failed to persist stage transition to backend:", err);
    }
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
            Real-time stage tracking with audit logs and persisted pipeline states.
          </p>
        </div>
      </div>

      {/* Kanban Board Horizontal Scroll */}
      <div className="flex gap-4 overflow-x-auto pb-4 items-start min-h-[600px]">
        {stages.map((col) => {
          const colApps = applications.filter(a => a.status === col.id || (col.id === "INTERVIEW" && a.status === "INTERVIEWING") || (col.id === "OFFER" && a.status === "OFFERED") || (col.id === "REJECTED" && a.status === "WITHDRAWN"));
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
                    {colApps.length}
                  </span>
                </div>
              </div>

              {/* Application Cards */}
              <div className="flex flex-col gap-3">
                {colApps.map((app) => (
                  <div
                    key={app.id}
                    className="p-4 rounded-xl glass-card border border-surface-border space-y-3 hover:border-surface-borderHover transition-all group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-gray-300 flex items-center gap-1">
                          <Building className="w-3 h-3 text-gray-400" /> {app.companyName}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded uppercase font-semibold bg-surface-elevated text-gray-400 border border-surface-border">
                          {app.atsType}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-white group-hover:text-primary-300 transition-colors">
                        {app.title}
                      </h3>
                      <div className="text-[11px] text-gray-400 mt-0.5">{app.salary}</div>
                    </div>

                    {app.notes && (
                      <p className="text-[11px] text-gray-300 bg-surface/60 p-2 rounded border border-surface-border leading-relaxed line-clamp-2">
                        {app.notes}
                      </p>
                    )}

                    {/* Footer Actions / Proof Badge */}
                    <div className="pt-2 border-t border-surface-border flex items-center justify-between text-xs">
                      {app.status === "QUEUED_FOR_APPROVAL" ? (
                        <button
                          onClick={() => onApprove(app.id)}
                          className="w-full py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-all"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" /> Approve for Submission
                        </button>
                      ) : app.status === "APPROVED" ? (
                        <div className="flex items-center gap-1 text-[11px] text-cyan-300">
                          <Clock className="w-3.5 h-3.5" /> Awaiting supervised submission
                        </div>
                      ) : app.status === "APPLIED" ? (
                        <div className="flex items-center justify-between w-full">
                          <span className="text-[11px] text-emerald-400 flex items-center gap-1 font-medium">
                            <CheckCircle2 className="w-3 h-3" /> Submitted
                          </span>
                          {app.proofScreenshotUrl && (
                            <button
                              onClick={() => setProofModalUrl(app.proofScreenshotUrl)}
                              className="text-[10px] text-primary-400 hover:text-primary-300 font-semibold flex items-center gap-1"
                            >
                              <ImageIcon className="w-3 h-3" /> View Proof
                            </button>
                          )}
                        </div>
                      ) : (
                        <div className="flex items-center justify-between w-full text-[11px] text-gray-400">
                          <span>Stage: {app.status}</span>
                          <button
                            onClick={() => onOpenTailoring({ companyName: app.companyName, title: app.title })}
                            className="text-primary-400 hover:text-primary-300"
                          >
                            Tailor
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {colApps.length === 0 && (
                  <div className="p-8 text-center border border-dashed border-surface-border rounded-xl text-xs text-gray-500">
                    No roles in this stage
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Proof Modal */}
      {proofModalUrl && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-elevated border border-surface-border max-w-3xl w-full rounded-2xl overflow-hidden shadow-2xl space-y-4 p-5">
            <div className="flex items-center justify-between border-b border-surface-border pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-emerald-400" /> Verified Submission Proof
              </h3>
              <button
                onClick={() => setProofModalUrl(null)}
                className="text-gray-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="max-h-[60vh] overflow-auto rounded-lg border border-surface-border bg-black">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={proofModalUrl}
                alt="Automated Submission Proof"
                className="w-full h-auto object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
