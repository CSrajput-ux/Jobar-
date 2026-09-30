import time
import random
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field

class PolicyDecision(BaseModel):
    allowed: bool
    effective_mode: str  # "DRAFT_ONLY", "APPROVE_THEN_SEND", "AUTO_SEND"
    requires_approval: bool
    reason: str
    scheduled_send_time: Optional[float] = None
    warmup_cap: int
    sent_today: int

class SendingPolicyEngine:
    """
    Sending Policy Engine for JobPilot Google Workspace Integration.
    Enforces:
    1. Sending modes (Draft-only default, Approve-then-send, Auto-send low risk only).
    2. Warm-up schedule (10 -> 20 -> 30 -> 40-50/day hard cap).
    3. Mandatory human quarantine: offers, salary/equity, legal, visa/sponsorship, low confidence.
    4. Quiet hours by recipient timezone (default: 9 PM - 8 AM).
    5. Anti-burst rate limiting: minimum 60s gap + random 10-30s jitter.
    6. Suppression list and bounce handling (detect 5xx bounces, parse mailer-daemon).
    7. Global automation kill switch.
    """

    SENSITIVE_TOPICS = [
        "salary", "compensation", "equity", "offer", "package", "signing bonus",
        "visa", "sponsorship", "h1b", "greencard", "work authorization",
        "contract", "nda", "legal", "background check", "criminal", "reference"
    ]

    BOUNCE_PATTERNS = [
        r"mail\s*delivery\s*subsystem",
        r"delivery\s*status\s*notification",
        r"undeliverable",
        r"550\s+5\.1\.1",
        r"user\s*unknown",
        r"address\s*not\s*found",
        r"message\s*rejected",
        r"returned\s*mail"
    ]

    def __init__(self):
        # Global kill switch flag
        self._automation_paused: bool = False

        # In-memory tracking for day sends: (account_id, date_str) -> count
        self._daily_send_counts: Dict[str, int] = {}

        # Last send timestamp per account for jitter & gap enforcement
        self._last_send_timestamp: Dict[str, float] = {}

        # Suppression list: email -> reason
        self._suppression_list: Dict[str, Dict[str, Any]] = {
            "spam-trap@company.com": {"reason": "HARD_BOUNCE", "addedAt": "2026-09-01T00:00:00Z"},
            "unsubscribed.recruiter@agency.com": {"reason": "USER_UNSUBSCRIBE", "addedAt": "2026-09-10T00:00:00Z"}
        }

    # =========================================================================
    # 1. KILL SWITCH
    # =========================================================================
    def is_paused(self) -> bool:
        return self._automation_paused

    def set_pause(self, paused: bool) -> bool:
        self._automation_paused = paused
        return self._automation_paused

    # =========================================================================
    # 2. WARM-UP RAMP & DAILY LIMITS
    # =========================================================================
    def get_warmup_cap(self, account_created_days_ago: int, user_configured_limit: int = 50) -> int:
        """
        Calculates daily cap based on mailbox age / warm-up schedule.
        - Days 0-3: 10 emails/day
        - Days 4-7: 20 emails/day
        - Days 8-14: 30 emails/day
        - Days 15+: 40-50 emails/day hard cap (personal Gmail limits)
        """
        if account_created_days_ago <= 3:
            schedule_max = 10
        elif account_created_days_ago <= 7:
            schedule_max = 20
        elif account_created_days_ago <= 14:
            schedule_max = 30
        else:
            schedule_max = 50

        return min(schedule_max, max(1, user_configured_limit))

    def get_daily_sends(self, account_id: str) -> int:
        today_key = f"{account_id}:{time.strftime('%Y-%m-%d', time.gmtime())}"
        return self._daily_send_counts.get(today_key, 0)

    def record_send(self, account_id: str):
        today_key = f"{account_id}:{time.strftime('%Y-%m-%d', time.gmtime())}"
        self._daily_send_counts[today_key] = self.get_daily_sends(account_id) + 1
        self._last_send_timestamp[account_id] = time.time()

    # =========================================================================
    # 3. QUIET HOURS (RECIPIENT TIMEZONE)
    # =========================================================================
    def is_in_quiet_hours(
        self,
        recipient_tz: str = "America/New_York",
        quiet_start_hour: int = 21,  # 9 PM
        quiet_end_hour: int = 8      # 8 AM
    ) -> Tuple[bool, Optional[float]]:
        """
        Returns (is_quiet, next_available_timestamp).
        Prevents sending emails outside recipient business/waking hours.
        """
        try:
            tz = ZoneInfo(recipient_tz)
        except Exception:
            tz = ZoneInfo("UTC")

        now_tz = datetime.now(tz)
        current_hour = now_tz.hour

        # Check if in quiet window
        in_quiet = False
        if quiet_start_hour > quiet_end_hour:
            # Over midnight (e.g. 21 to 8)
            if current_hour >= quiet_start_hour or current_hour < quiet_end_hour:
                in_quiet = True
        else:
            if quiet_start_hour <= current_hour < quiet_end_hour:
                in_quiet = True

        if not in_quiet:
            return False, None

        import datetime as dt
        # Calculate next waking slot: tomorrow or today at quiet_end_hour + small random offset
        if current_hour >= quiet_start_hour:
            next_morning = now_tz.replace(hour=quiet_end_hour, minute=random.randint(5, 25), second=0, microsecond=0)
            next_morning = next_morning + dt.timedelta(days=1)
        else:
            next_morning = now_tz.replace(hour=quiet_end_hour, minute=random.randint(5, 25), second=0, microsecond=0)

        return True, next_morning.timestamp()

    # =========================================================================
    # 4. SENSITIVITY & APPROVAL QUARANTINE
    # =========================================================================
    def check_sensitive_content(self, subject: str, body: str, category: str = "") -> Tuple[bool, List[str]]:
        """
        Quarantines offers, compensation, legal, or visa-related messages.
        These MUST NEVER be auto-sent without explicit candidate sign-off.
        """
        combined = f"{subject} {body} {category}".lower()
        matched = [topic for topic in self.SENSITIVE_TOPICS if topic in combined]
        if category.lower() in ["offer", "legal", "visa"]:
            if category.lower() not in matched:
                matched.append(category.lower())
        return len(matched) > 0, matched

    # =========================================================================
    # 5. SUPPRESSION LIST & BOUNCE HANDLING
    # =========================================================================
    def is_suppressed(self, recipient_email: str) -> Tuple[bool, Optional[str]]:
        clean_email = recipient_email.strip().lower()
        record = self._suppression_list.get(clean_email)
        if record:
            return True, record.get("reason", "SUPPRESSED")
        return False, None

    def add_to_suppression(self, recipient_email: str, reason: str):
        clean_email = recipient_email.strip().lower()
        self._suppression_list[clean_email] = {
            "reason": reason,
            "addedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def detect_and_handle_bounce(self, subject: str, sender: str, body: str) -> Optional[str]:
        """
        Detects delivery failure notices (DSN, 550, Mailer-Daemon).
        Extracts bounced recipient and automatically adds to suppression list.
        """
        combined = f"{subject} {sender} {body}".lower()
        is_bounce = any(re.search(pat, combined) for pat in self.BOUNCE_PATTERNS)
        if not is_bounce:
            return None

        # Extract failed email address from body or headers
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', body)
        bounced_email = email_match.group(0).lower() if email_match else None

        if bounced_email and "jobpilot" not in bounced_email:
            self.add_to_suppression(bounced_email, "AUTOMATIC_BOUNCE_DETECTED")
            return bounced_email
        return None

    # =========================================================================
    # 6. MASTER DECISION ENGINE
    # =========================================================================
    def evaluate_outbound_email(
        self,
        account_id: str,
        recipient_email: str,
        subject: str,
        body: str,
        category: str = "outreach",
        confidence: float = 0.95,
        user_mode: str = "DRAFT_ONLY",
        account_age_days: int = 14,
        recipient_tz: str = "America/New_York",
        user_daily_limit: int = 40
    ) -> PolicyDecision:
        """
        Evaluates an outbound email against all policy rules.
        Guarantees safety and prevents unauthorized or out-of-bounds sends.
        """
        # 1. Global Kill Switch Check
        if self._automation_paused:
            return PolicyDecision(
                allowed=False,
                effective_mode="DRAFT_ONLY",
                requires_approval=True,
                reason="Global automation kill switch is ACTIVE. Outbound emails paused.",
                warmup_cap=0,
                sent_today=self.get_daily_sends(account_id)
            )

        # 2. Suppression List Check
        suppressed, reason = self.is_suppressed(recipient_email)
        if suppressed:
            return PolicyDecision(
                allowed=False,
                effective_mode="DRAFT_ONLY",
                requires_approval=True,
                reason=f"Recipient {recipient_email} is on suppression list ({reason}). Send blocked.",
                warmup_cap=0,
                sent_today=self.get_daily_sends(account_id)
            )

        # 3. Daily Cap & Warm-up Ramp Check
        warmup_cap = self.get_warmup_cap(account_age_days, user_daily_limit)
        sent_today = self.get_daily_sends(account_id)
        if sent_today >= warmup_cap:
            return PolicyDecision(
                allowed=False,
                effective_mode="DRAFT_ONLY",
                requires_approval=True,
                reason=f"Daily warm-up cap reached ({sent_today}/{warmup_cap} emails today). Queued for tomorrow.",
                warmup_cap=warmup_cap,
                sent_today=sent_today
            )

        # 4. Sensitive Topic & Low Confidence Quarantine
        is_sensitive, matched_topics = self.check_sensitive_content(subject, body, category)
        is_low_confidence = confidence < 0.85

        effective_mode = user_mode.upper()
        requires_approval = False

        if effective_mode == "DRAFT_ONLY":
            requires_approval = True
            decision_reason = "Draft-only mode is active (default). Draft created for user review in Gmail."
        elif is_sensitive:
            effective_mode = "APPROVE_THEN_SEND"
            requires_approval = True
            decision_reason = f"Contains sensitive topics ({', '.join(matched_topics)}). Mandatory human approval required."
        elif is_low_confidence:
            effective_mode = "APPROVE_THEN_SEND"
            requires_approval = True
            decision_reason = f"AI confidence score ({confidence:.2f}) is below threshold 0.85. Human review required."
        elif effective_mode == "APPROVE_THEN_SEND":
            requires_approval = True
            decision_reason = "Approve-then-send policy active. Waiting for candidate confirmation."
        else:
            # AUTO_SEND (low risk verified)
            decision_reason = "Low risk routine outreach approved for auto-send."

        # 5. Quiet Hours & Scheduling Jitter
        is_quiet, next_morning_ts = self.is_in_quiet_hours(recipient_tz)
        
        # Calculate anti-burst jitter: minimum 60 seconds from last send + 10-30s random jitter
        last_send = self._last_send_timestamp.get(account_id, 0)
        gap_delay = max(0.0, (last_send + 60.0 + random.uniform(10.0, 30.0)) - time.time())
        
        scheduled_send_time = time.time() + gap_delay
        if is_quiet and next_morning_ts:
            scheduled_send_time = max(scheduled_send_time, next_morning_ts)
            decision_reason += f" Scheduled after recipient quiet hours ({recipient_tz})."

        return PolicyDecision(
            allowed=True,
            effective_mode=effective_mode,
            requires_approval=requires_approval,
            reason=decision_reason,
            scheduled_send_time=scheduled_send_time,
            warmup_cap=warmup_cap,
            sent_today=sent_today
        )

policy_engine = SendingPolicyEngine()
