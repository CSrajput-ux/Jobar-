"use client";

import React, { useState } from "react";
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

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [killSwitchActive, setKillSwitchActive] = useState(false);
  const [selectedJobForTailoring, setSelectedJobForTailoring] = useState<any>(null);

  const handleApproveApplication = (appId: string) => {
    alert("Application approved! Playwright runner dispatched with proof screenshot capture.");
  };

  const handleTailorAndApply = (job: any) => {
    setSelectedJobForTailoring(job);
    setActiveTab("tailoring");
  };

  const handleSaveJob = (job: any) => {
    alert(`Saved ${job.title} at ${job.companyName} to your pipeline.`);
  };

  return (
    <div className="flex min-h-screen bg-background text-gray-100">
      {/* Fixed Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        pendingApprovalsCount={1}
        unreadInboxCount={1}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          killSwitchActive={killSwitchActive}
          onToggleKillSwitch={setKillSwitchActive}
          activeTab={activeTab}
        />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {activeTab === "overview" && (
            <OverviewView
              onNavigate={setActiveTab}
              onApproveApplication={handleApproveApplication}
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
            />
          )}

          {activeTab === "approval" && (
            <ApprovalQueueView
              onApproveApplication={handleApproveApplication}
              onOpenTailoring={handleTailorAndApply}
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
              onToggleKillSwitch={setKillSwitchActive}
            />
          )}
        </main>
      </div>
    </div>
  );
}
