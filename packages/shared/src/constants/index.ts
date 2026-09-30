import { ApplicationStatus, EmailClassification } from '../types/index.js';

export const KANBAN_STAGES: { id: ApplicationStatus; title: string; color: string }[] = [
  { id: 'SAVED', title: 'Saved Jobs', color: 'slate' },
  { id: 'QUEUED_FOR_APPROVAL', title: 'Approval Queue', color: 'amber' },
  { id: 'APPLYING', title: 'Applying...', color: 'blue' },
  { id: 'APPLIED', title: 'Applied', color: 'indigo' },
  { id: 'NEEDS_ATTENTION', title: 'Needs Attention', color: 'rose' },
  { id: 'INTERVIEW', title: 'Interviews', color: 'emerald' },
  { id: 'OFFER', title: 'Offers', color: 'purple' },
  { id: 'REJECTED', title: 'Archived / Rejected', color: 'zinc' },
];

export const EMAIL_CLASSIFICATION_META: Record<EmailClassification, { label: string; badgeVariant: string; icon: string }> = {
  INTERVIEW_INVITE: { label: 'Interview Invitation', badgeVariant: 'emerald', icon: 'Calendar' },
  ASSESSMENT: { label: 'Online Assessment', badgeVariant: 'blue', icon: 'Code' },
  QUESTION: { label: 'Recruiter Follow-up', badgeVariant: 'purple', icon: 'MessageCircle' },
  OFFER: { label: 'Job Offer', badgeVariant: 'gold', icon: 'Sparkles' },
  REJECTION: { label: 'Rejection', badgeVariant: 'rose', icon: 'XCircle' },
  IRRELEVANT: { label: 'Newsletter / Auto-reply', badgeVariant: 'zinc', icon: 'Mail' },
};

export const DEFAULT_PREFERENCES = {
  dailyApplyCap: 15,
  minMatchScore: 75,
  visaSponsorshipRequired: false,
  applyMode: 'APPROVAL_QUEUE' as const,
  workModes: ['remote', 'hybrid'] as const,
};

export const SYSTEM_LIMITS = {
  MAX_DAILY_OUTREACH: 40,
  INITIAL_OUTREACH_WARMUP_DAILY: 10,
  MAX_HOURLY_APPLICATIONS_PER_DOMAIN: 3,
  MATCH_SCORE_AUTO_APPLY_MINIMUM: 80,
  LOW_CONFIDENCE_THRESHOLD: 0.85,
};
