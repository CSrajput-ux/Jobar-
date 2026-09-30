"use client";

import React from "react";
import { 
  Compass, 
  Briefcase, 
  Layers, 
  CheckSquare, 
  FileText, 
  Send, 
  Inbox, 
  Calendar as CalendarIcon, 
  Sliders, 
  Sparkles,
  Zap,
  ShieldCheck,
  Globe2,
  Mail
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  pendingApprovalsCount?: number;
  unreadInboxCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  pendingApprovalsCount = 1,
  unreadInboxCount = 1
}) => {
  const navItems = [
    { id: "overview", label: "Dashboard", icon: Compass },
    { id: "jobs", label: "Job Discovery", icon: Briefcase, badge: "Live" },
    { id: "kanban", label: "Pipeline Kanban", icon: Layers },
    { id: "approval", label: "Approval Queue", icon: CheckSquare, badge: pendingApprovalsCount > 0 ? `${pendingApprovalsCount}` : undefined, badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30" },
    { id: "tailoring", label: "Resume Studio", icon: FileText, badge: "AI" },
    { id: "outreach", label: "Cold Outreach", icon: Send },
    { id: "inbox", label: "Inbox Intelligence", icon: Inbox, badge: unreadInboxCount > 0 ? "1 Invite" : undefined, badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
    { id: "calendar", label: "Interviews & GCal", icon: CalendarIcon },
    { id: "google", label: "Google Workspace", icon: Mail, badge: "CASA 2", badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
    { id: "sources", label: "Global Coverage", icon: Globe2, badge: "104 Cntr", badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
    { id: "settings", label: "Profile & Settings", icon: Sliders },
  ];

  return (
    <aside className="w-64 border-r border-surface-border bg-surface flex flex-col justify-between h-screen sticky top-0 z-40 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center gap-3 border-b border-surface-border">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary-600 via-primary-500 to-accent-violet flex items-center justify-center shadow-glow-primary">
            <Zap className="w-5 h-5 text-white fill-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-base tracking-tight text-white">JobPilot</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400 border border-primary-500/30">
                PRO
              </span>
            </div>
            <div className="text-[11px] text-gray-400">Autonomous Job Search</div>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-primary-600/15 text-primary-400 border border-primary-500/30 font-semibold shadow-sm"
                    : "text-gray-400 hover:text-gray-200 hover:bg-surface-elevated/60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? "text-primary-400" : "text-gray-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${
                      item.badgeColor || "bg-primary-500/20 text-primary-300 border-primary-500/30"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security & Token Banner */}
      <div className="p-4 border-t border-surface-border bg-surface-elevated/40 m-3 rounded-xl border">
        <div className="flex items-center gap-2 mb-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="text-[11px] font-semibold text-gray-200">Security Vault</span>
        </div>
        <p className="text-[10px] text-gray-400 leading-relaxed mb-3">
          OAuth credentials & PII encrypted with AES-256-GCM. Human-in-the-loop approval active.
        </p>
        <div className="flex items-center justify-between text-[10px] text-gray-400">
          <span>Apply Mode</span>
          <span className="text-amber-400 font-semibold bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
            Approval Queue
          </span>
        </div>
      </div>
    </aside>
  );
};
