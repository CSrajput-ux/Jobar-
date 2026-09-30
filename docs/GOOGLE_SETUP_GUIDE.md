# Google Cloud Platform Setup & OAuth 2.0 Verification Guide

This guide provides end-to-end instructions for setting up Google Cloud Platform credentials, configuring OAuth 2.0 with PKCE, setting up Cloud Pub/Sub for real-time Gmail push notifications, and navigating Google's **Sensitive & Restricted Scope Verification** (including the CASA assessment).

---

## 1. Google Cloud Project Setup

### Step 1: Create Project & Enable APIs
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown in the top bar and select **New Project**.
   - Project Name: `JobPilot-Production` (or `JobPilot-Dev`)
3. Navigate to **APIs & Services > Library**.
4. Search for and enable the following three APIs:
   - **Gmail API**
   - **Google Calendar API**
   - **Cloud Pub/Sub API**

---

## 2. OAuth Consent Screen Configuration

1. In the left navigation, go to **APIs & Services > OAuth consent screen**.
2. Select **External** user type and click **Create**.
3. **App Information:**
   - App name: `JobPilot`
   - User support email: `support@jobpilot.dev` (or your developer email)
   - App logo: 120x120px PNG icon
4. **App Domain:**
   - Application home page: `https://jobpilot.dev` (or `http://localhost:3000` for development)
   - Application privacy policy link: `https://jobpilot.dev/privacy`
   - Application terms of service link: `https://jobpilot.dev/terms`
   - Authorized domains: `jobpilot.dev` (for local test mode, leave blank or use localhost)
5. **Scopes Declaration:**
   Click **Add or Remove Scopes** and add:
   - Non-Sensitive: `openid`, `.../auth/userinfo.email`, `.../auth/userinfo.profile`
   - Sensitive (Calendar): `https://www.googleapis.com/auth/calendar.events`, `https://www.googleapis.com/auth/calendar.freebusy`
   - Restricted (Gmail): `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.compose`
6. **Test Users:**
   In Development / Testing mode, add up to 100 test user Gmail accounts (e.g. `your-email@gmail.com`). These accounts can authorize the app immediately without waiting for Google verification.

---

## 3. OAuth 2.0 Client Credentials

1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Application type: **Web application**.
4. Name: `JobPilot Web & API Client`.
5. **Authorized JavaScript origins:**
   - `http://localhost:3000`
   - `https://jobpilot.dev`
6. **Authorized redirect URIs:**
   - Development: `http://localhost:8000/api/v1/auth/google/callback`
   - Production: `https://api.jobpilot.dev/api/v1/auth/google/callback`
7. Click **Create** and copy your `Client ID` and `Client Secret` into `.env`:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret
   ```

---

## 4. Cloud Pub/Sub Topic & Push Subscription (Real-Time Gmail Sync)

1. Go to **Cloud Pub/Sub > Topics** in Google Cloud Console.
2. Click **Create Topic**:
   - Topic ID: `jobpilot-gmail-watch`
3. Click the topic name, then go to the **Permissions** tab:
   - Click **Add Principal**.
   - New principal: `gmail-api-push@system.gserviceaccount.com`
   - Role: **Pub/Sub Publisher**.
   - Click **Save**. (This grants the Gmail system permission to post notifications when new emails arrive).
4. Go to **Subscriptions > Create Subscription**:
   - Subscription ID: `jobpilot-gmail-push-sub`
   - Delivery type: **Push**
   - Endpoint URL: `https://api.jobpilot.dev/api/v1/gmail/webhook` (or tunnel like ngrok for local dev)
   - Enable authentication: **Create Service Account** with JWT token validation.

---

## 5. Google Verification & CASA Assessment Package

When moving from Test Mode to Public Production, Google requires verification for sensitive and restricted scopes.

### Scope Justification Text for Google Review Team
* **`gmail.readonly`**:
  > *"JobPilot requests `gmail.readonly` solely to detect incoming communications from recruiters and employers regarding job applications submitted by the user. The app automatically filters non-job emails and only processes relevant messages to classify application stages (e.g. interview invitations, rejections, assessments). No user email is used for advertising or model training."*
* **`gmail.send` & `gmail.compose`**:
  > *"Requested to enable users to draft and send job application follow-ups and reply to recruiters directly from their authentic personal mailbox. Sending adheres to strict user-configured policies, warmup throttles, and defaults to human review."*
* **`calendar.events` & `calendar.freebusy`**:
  > *"Requested to identify conflict-free availability windows and automatically create Google Meet calendar invitations when a recruiter invites the candidate to an interview."*

### Demo Video Script Checklist
1. **0:00 - 0:25**: Show Google OAuth consent screen with client ID clearly visible in the URL bar.
2. **0:25 - 0:50**: Show user granting incremental scopes with in-app explanation modal.
3. **0:50 - 1:30**: Demonstrate incoming interview invite detection and thread classification.
4. **1:30 - 2:00**: Show candidate approving a drafted reply and sending via `gmail.send`.
5. **2:00 - 2:30**: Show conflict-free slot proposal and Google Meet calendar event creation.
6. **2:30 - 3:00**: Show user navigating to Settings, clicking **"Disconnect Google"** and **"Delete All Stored Data"**, demonstrating complete token revocation.

### Cloud Application Security Assessment (CASA) Readiness
- [x] Tier 2/3 Self-Assessment questionnaire completed.
- [x] Tokens encrypted at rest with AES-256-GCM.
- [x] TLS 1.3 enforced for all external network endpoints.
- [x] Dependency vulnerability scanning with clean audit records.
- [x] Strict data retention limits (purging inactive tokens and non-job metadata).
