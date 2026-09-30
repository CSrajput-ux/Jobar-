export type UUID = string;

export type ATSPlatform = 'greenhouse' | 'lever' | 'ashby' | 'workable' | 'remotive' | 'custom';

export type WorkMode = 'remote' | 'hybrid' | 'onsite';

export type ApplyMode = 'MANUAL' | 'APPROVAL_QUEUE' | 'FULL_AUTO';

export type ApplicationStatus = 
  | 'SAVED'
  | 'QUEUED_FOR_APPROVAL'
  | 'APPLYING'
  | 'APPLIED'
  | 'NEEDS_ATTENTION'
  | 'REJECTED'
  | 'INTERVIEW'
  | 'OFFER';

export type EmailClassification =
  | 'INTERVIEW_INVITE'
  | 'REJECTION'
  | 'ASSESSMENT'
  | 'OFFER'
  | 'QUESTION'
  | 'IRRELEVANT';

export interface User {
  id: UUID;
  email: string;
  fullName: string;
  isActive: boolean;
  killSwitchActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ExperienceItem {
  id: string;
  company: string;
  title: string;
  startDate: string;
  endDate?: string;
  isCurrent: boolean;
  location?: string;
  highlights: string[];
  skillsUsed: string[];
}

export interface EducationItem {
  id: string;
  institution: string;
  degree: string;
  fieldOfStudy: string;
  startDate: string;
  endDate?: string;
}

export interface ProjectItem {
  id: string;
  name: string;
  description: string;
  role?: string;
  url?: string;
  technologies: string[];
}

export interface StructuredProfile {
  headline: string;
  summary: string;
  phone?: string;
  location: string;
  linkedinUrl?: string;
  githubUrl?: string;
  portfolioUrl?: string;
  skills: {
    technical: string[];
    frameworks: string[];
    tools: string[];
    languages: string[];
  };
  experience: ExperienceItem[];
  education: EducationItem[];
  projects: ProjectItem[];
}

export interface CommonApplicationAnswers {
  noticePeriodDays: number;
  workAuthorizationStatus: string;
  requiresSponsorship: boolean;
  expectedSalaryUsd: number;
  whyThisCompanyDefault?: string;
  genderPronouns?: string;
  veteranStatus?: string;
  disabilityStatus?: string;
}

export interface UserPreferences {
  targetRoles: string[];
  seniorityLevels: string[];
  locations: string[];
  workModes: WorkMode[];
  minSalaryUsd?: number;
  visaSponsorshipRequired: boolean;
  blacklistedCompanies: string[];
  targetIndustries: string[];
  applyMode: ApplyMode;
  dailyApplyCap: number;
  minMatchScore: number;
}

export interface Job {
  id: UUID;
  companyId?: UUID;
  companyName: string;
  title: string;
  location: string;
  workMode: WorkMode;
  descriptionText: string;
  requirementsText?: string;
  salaryRange?: string;
  source: string;
  externalUrl: string;
  dedupHash: string;
  atsType?: ATSPlatform;
  postedAt?: string;
  createdAt: string;
}

export interface MatchReasoning {
  score: number;
  matchedSkills: string[];
  missingSkills: string[];
  redFlags: string[];
  fitSummary: string;
  seniorityAlignment: 'underqualified' | 'ideal' | 'overqualified';
}

export interface TailoredBulletDiff {
  original: string;
  tailored: string;
  targetSkillHighlight?: string;
}

export interface TailoredResumeData {
  targetRole: string;
  companyName: string;
  summary: string;
  bulletDiffs: TailoredBulletDiff[];
  tailoredExperience: ExperienceItem[];
  matchingCoverLetter: string;
  pdfUrl?: string;
}

export interface JobMatch {
  id: UUID;
  userId: UUID;
  jobId: UUID;
  score: number;
  reasoning: MatchReasoning;
  tailoredResume?: TailoredResumeData;
  createdAt: string;
}

export interface Application {
  id: UUID;
  userId: UUID;
  jobId: UUID;
  job?: Job;
  status: ApplicationStatus;
  appliedAt?: string;
  proofScreenshotUrl?: string;
  submittedPayload?: Record<string, any>;
  failureReason?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ApplicationEvent {
  id: UUID;
  applicationId: UUID;
  eventType: 'STATUS_CHANGE' | 'FORM_ATTEMPT' | 'CAPTCHA_BLOCKED' | 'CONFIRMATION_RECEIVED' | 'USER_OVERRIDE';
  metadata: Record<string, any>;
  createdAt: string;
}

export interface RecruiterContact {
  id: UUID;
  companyId: UUID;
  companyName: string;
  fullName: string;
  email: string;
  roleTitle?: string;
  linkedinUrl?: string;
  isVerified: boolean;
}

export interface OutreachCampaign {
  id: UUID;
  userId: UUID;
  applicationId?: UUID;
  contactId: UUID;
  contact?: RecruiterContact;
  status: 'DRAFT' | 'SCHEDULED' | 'ACTIVE' | 'COMPLETED' | 'PAUSED_ON_REPLY';
  createdAt: string;
}

export interface OutreachEmail {
  id: UUID;
  campaignId: UUID;
  sequenceStep: number;
  subject: string;
  bodyText: string;
  status: 'PENDING_APPROVAL' | 'QUEUED' | 'SENT' | 'OPENED' | 'REPLIED';
  scheduledSendAt?: string;
  sentAt?: string;
}

export interface EmailThreadItem {
  id: UUID;
  userId: UUID;
  applicationId?: UUID;
  gmailThreadId: string;
  subject: string;
  fromAddress: string;
  lastMessageAt: string;
  classification: EmailClassification;
  summarySnippet: string;
  needsAttention: boolean;
}

export interface CalendarEventItem {
  id: UUID;
  userId: UUID;
  applicationId?: UUID;
  googleEventId: string;
  summary: string;
  startTime: string;
  endTime: string;
  meetLink?: string;
  recruiterEmail?: string;
}
