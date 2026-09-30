"use client";

import React, { useState } from "react";
import { 
  Shield, 
  Power, 
  Mail, 
  Calendar, 
  Bell, 
  Search, 
  Sparkles,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";

interface HeaderProps {
  killSwitchActive: boolean;
  onToggleKillSwitch: (active: boolean) => void;
  activeTab: string;
}

export const Header: React.FC<HeaderProps> = ({
  killSwitchActive,
  onToggleKillSwitch,
  activeTab
}) => {
  return (
    <header className="h-16 border-b border-surface-border bg-surface/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Search / Context bar */}
      <div className="flex items-center gap-4 flex-1 max-w-xl">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search discovered jobs, recruiters, applications, or notes..."
            className="w-full pl-10 pr-4 py-2 bg-background/60 border border-surface-border rounded-lg text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
          />
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {/* Google Integrations Status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-elevated border border-surface-border text-xs text-gray-300">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <Mail className="w-3.5 h-3.5 text-emerald-400" />
          <span>Gmail Synced</span>
          <span className="text-gray-600">|</span>
          <Calendar className="w-3.5 h-3.5 text-blue-400" />
          <span>GCal Active</span>
        </div>

        {/* Emergency Kill Switch Button */}
        <button
          onClick={() => onToggleKillSwitch(!killSwitchActive)}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
            killSwitchActive
              ? "bg-rose-500/20 text-rose-300 border-rose-500/50 hover:bg-rose-500/30 animate-pulse"
              : "bg-surface-elevated text-gray-300 border-surface-border hover:border-gray-600 hover:text-white"
          }`}
          title={killSwitchActive ? "Automation Paused. Click to Resume." : "Emergency Kill Switch. Click to halt all automated tasks immediately."}
        >
          <Power className={`w-3.5 h-3.5 ${killSwitchActive ? "text-rose-400" : "text-gray-400"}`} />
          <span>{killSwitchActive ? "PAUSED (KILL SWITCH)" : "Kill Switch"}</span>
        </button>

        {/* User Profile avatar */}
        <div className="flex items-center gap-3 pl-3 border-l border-surface-border">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-600 to-accent-violet flex items-center justify-center text-xs font-bold text-white shadow-glow-primary">
            AC
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-gray-200">Alex Chen</div>
            <div className="text-[10px] text-gray-400">Staff Full-Stack</div>
          </div>
        </div>
      </div>
    </header>
  );
};
