import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobPilot — Autonomous AI Job Search & Application Platform",
  description: "Automate your entire job hunt: discovery across Greenhouse/Lever, zero-fabrication resume tailoring, 1-click auto-apply, recruiter cold outreach, inbox sync, and Google Calendar scheduling.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-gray-100 antialiased selection:bg-primary-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
