"use client";

import React, { useState } from "react";
import { 
  Calendar as CalendarIcon, 
  Clock, 
  Video, 
  User, 
  CheckCircle2, 
  ExternalLink, 
  Plus, 
  Sparkles,
  CalendarCheck
} from "lucide-react";

export const CalendarView: React.FC = () => {
  const [scheduledEvents, setScheduledEvents] = useState([
    {
      id: "60000000-0000-0000-0000-000000000001",
      companyName: "Supabase",
      role: "Backend Engineer, Postgres & Vector Engine",
      summary: "Technical Intro: Backend Engineer @ Supabase",
      dateStr: "Friday, October 2, 2026",
      timeStr: "11:00 AM - 11:45 AM PT",
      meetLink: "https://meet.google.com/sup-eng-intro",
      recruiter: "Elena Rostova (elena.r@supabase.com)"
    }
  ]);

  const [proposedSlots, setProposedSlots] = useState([
    { id: 1, label: "Thursday, Oct 1 • 10:00 AM - 10:45 AM PT", status: "Conflict-Free" },
    { id: 2, label: "Thursday, Oct 1 • 1:00 PM - 1:45 PM PT", status: "Conflict-Free" },
    { id: 3, label: "Friday, Oct 2 • 11:00 AM - 11:45 AM PT", status: "Conflict-Free (Selected)" }
  ]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <CalendarIcon className="w-5 h-5 text-primary-400" />
            Interview Scheduler & Google Calendar
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Autonomous conflict-free scheduling with Google Calendar API. Proposes 3 slots in recruiter timezone and creates Google Meet links.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-elevated border border-surface-border text-xs text-gray-300">
          <CalendarCheck className="w-4 h-4 text-blue-400" />
          <span>GCal API: Synced</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Upcoming Confirmed Interviews */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Confirmed Interview Calendar
          </h3>

          <div className="space-y-3">
            {scheduledEvents.map((event) => (
              <div
                key={event.id}
                className="p-5 rounded-2xl glass-card border border-emerald-500/30 bg-emerald-500/5 space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-gray-300">{event.companyName}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        Confirmed Meet Link
                      </span>
                    </div>
                    <h2 className="text-base font-bold text-white">{event.summary}</h2>
                    <p className="text-xs text-gray-400 mt-0.5">{event.role}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1 text-gray-300">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-emerald-400" />
                    <span>{event.dateStr} • {event.timeStr}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-400" />
                    <span>{event.recruiter}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-surface-border flex items-center justify-between">
                  <a
                    href={event.meetLink}
                    target="_blank"
                    rel="noreferrer"
                    className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-xs font-semibold shadow-glow-primary flex items-center gap-2 transition-all"
                  >
                    <Video className="w-4 h-4" />
                    Join Google Meet Call
                  </a>

                  <span className="text-[11px] text-gray-500">
                    Prep reminder set: 30m prior
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Automated 3-Slot Negotiator */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-primary-400" />
            3-Slot Availability Negotiator
          </h3>

          <div className="p-4 rounded-xl glass-panel border border-surface-border space-y-3">
            <p className="text-xs text-gray-400 leading-relaxed">
              When an interview email is received, JobPilot reads your Google Calendar free/busy slots and auto-proposes these 3 conflict-free windows:
            </p>

            <div className="space-y-2">
              {proposedSlots.map((slot) => (
                <div
                  key={slot.id}
                  className="p-3 rounded-lg bg-surface border border-surface-border text-xs space-y-1"
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-primary-300 font-bold">Slot #{slot.id}</span>
                    <span className="text-emerald-400 text-[10px] font-semibold">{slot.status}</span>
                  </div>
                  <div className="text-gray-200 font-medium">{slot.label}</div>
                </div>
              ))}
            </div>

            <div className="pt-2 text-[11px] text-gray-500 flex items-center justify-between">
              <span>Timezone:</span>
              <span className="text-gray-300 font-semibold">America/Los_Angeles (PT)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
