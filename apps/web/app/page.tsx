"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "../components/layout/Sidebar";
import { Header } from "../components/layout/Header";
import { OverviewView } from "../components/views/OverviewView";
import { JobDiscoveryView } from "../components/views/JobDiscoveryView";
import { ApplicationKanbanView } from "../components/views/ApplicationKanbanView";
import { ApprovalQueueView } from "../components/views/ApprovalQueueView";
import { TailoringStudioView } from "../components/views/TailoringStudioView";
import { OutreachView } from "../components/views/OutreachView";
import { InboxView } from "../components/views/InboxView";
import { CalendarView } from "../components/views/CalendarView";
import { GoogleIntegrationView } from "../components/views/GoogleIntegrationView";
import { SettingsView } from "../components/views/SettingsView";
import { SourcesAdminView } from "../components/views/SourcesAdminView";
import { api } from "../lib/api";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [killSwitchActive, setKillSwitchActive] = useState(false);
  const [selectedJobForTailoring, setSelectedJobForTailoring] = useState<any>(null);
  
  const [profile, setProfile] = useState<any>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [calendarEvents, setCalendarEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const refreshApplications = async () => {
    try {
      const data = await api.getApplications();
      if (Array.isArray(data)) setApplications(data);
    } catch (err) {
      console.warn("Failed to refresh applications:", err);
    }
  };

  const refreshAll = async () => {
    try {
      const [profRes, appsRes, jobsRes, calRes, secRes] = await Promise.allSettled([
        api.getProfile(),
        api.getApplications(),
        api.getJobs(),
        api.getCalendarEvents(),
        api.getSecurityStatus(),
      ]);

      if (profRes.status === "fulfilled") setProfile(profRes.value);
      if (appsRes.status === "fulfilled" && Array.isArray(appsRes.value)) setApplications(appsRes.value);
      if (jobsRes.status === "fulfilled" && Array.isArray(jobsRes.value)) setJobs(jobsRes.value);
      if (calRes.status === "fulfilled" && Array.isArray(calRes.value)) setCalendarEvents(calRes.value);
      if (secRes.status === "fulfilled") setKillSwitchActive(Boolean(secRes.value.killSwitchActive));
    } catch (err) {
      console.warn("Error bootstrapping dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAll();
  }, []);

  const handleApproveApplication = async (appId: string) => {
    try {
      await api.approveApplication(appId);
      await refreshApplications();
    } catch (err) {
      console.error("Failed to approve application:", err);
    }
  };

  const handleToggleKillSwitch = async (active: boolean) => {
    try {
      await api.toggleKillSwitch(active);
      setKillSwitchActive(active);
    } catch (err) {
      console.error("Failed to toggle kill switch:", err);
    }
  };

  const handleTailorAndApply = (job: any) => {
    setSelectedJobForTailoring(job);
    setActiveTab("tailoring");
  };

  const handleSaveJob = async (job: any) => {
    try {
      await api.createApplication(job.id, "SAVED");
      await refreshApplications();
    } catch (err) {
      console.error("Failed to save job to pipeline:", err);
    }
  };

  const pendingApprovalsCount = applications.filter(a => a.status === "QUEUED_FOR_APPROVAL").length;

  return (
    <div className="flex min-h-screen bg-background text-gray-100">
      {/* Fixed Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        pendingApprovalsCount={pendingApprovalsCount}
        unreadInboxCount={1}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          killSwitchActive={killSwitchActive}
          onToggleKillSwitch={handleToggleKillSwitch}
          activeTab={activeTab}
        />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {activeTab === "overview" && (
            <OverviewView
              onNavigate={setActiveTab}
              onApproveApplication={handleApproveApplication}
              profile={profile}
              applications={applications}
              jobs={jobs}
              calendarEvents={calendarEvents}
            />
          )}

          {activeTab === "jobs" && (
            <JobDiscoveryView
              onTailorAndApply={handleTailorAndApply}
              onSaveJob={handleSaveJob}
            />
          )}

          {activeTab === "kanban" && (
            <ApplicationKanbanView
              onApprove={handleApproveApplication}
              onOpenTailoring={handleTailorAndApply}
              initialApplications={applications}
              onRefresh={refreshApplications}
            />
          )}

          {activeTab === "approval" && (
            <ApprovalQueueView
              onApproveApplication={handleApproveApplication}
              onOpenTailoring={handleTailorAndApply}
              applications={applications.filter(a => a.status === "QUEUED_FOR_APPROVAL")}
              onRefresh={refreshApplications}
            />
          )}

          {activeTab === "tailoring" && (
            <TailoringStudioView
              initialJob={selectedJobForTailoring}
            />
          )}

          {activeTab === "outreach" && (
            <OutreachView />
          )}

          {activeTab === "inbox" && (
            <InboxView />
          )}

          {activeTab === "calendar" && (
            <CalendarView />
          )}

          {activeTab === "google" && (
            <GoogleIntegrationView />
          )}

          {activeTab === "sources" && (
            <SourcesAdminView />
          )}

          {activeTab === "settings" && (
            <SettingsView
              killSwitchActive={killSwitchActive}
              onToggleKillSwitch={handleToggleKillSwitch}
            />
          )}
        </main>
      </div>
    </div>
  );
}
