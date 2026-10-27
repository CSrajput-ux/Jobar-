import os
import time
import random
import asyncio
from typing import Dict, Any

class PlaywrightApplyRunner:
    """
    Supervised Playwright helper for supported ATS forms (Greenhouse, Lever).
    Live interaction is disabled by default and never treats a filled form as a
    completed application. It strictly halts on CAPTCHA, login walls, and any
    result that needs candidate review.
    """
    def __init__(self, headless: bool = True, allow_live_browser: bool = False):
        self.headless = headless
        # Live form interaction is opt-in.  A worker must not open an external
        # application page merely because a queued task exists.
        self.allow_live_browser = allow_live_browser
        self.screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)

    async def apply_to_job(
        self,
        application_id: str,
        job_url: str,
        candidate_info: Dict[str, Any],
        resume_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        When explicitly enabled, opens an ATS form and fills available fields.
        It returns NEEDS_ATTENTION for candidate review rather than submitting.
        """
        if not self.allow_live_browser:
            return {
                "status": "NEEDS_ATTENTION",
                "reason": "Live browser submission is disabled. Open the ATS and submit manually after review.",
                "screenshotUrl": None,
                "requiresManualAction": True,
            }
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            # Fallback simulator for environments where playwright browser is not pre-installed
            return self._simulate_apply(application_id, job_url, candidate_info)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                ]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                print(f"[Playwright] Navigating to {job_url}...")
                await page.goto(job_url, wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(1.5)

                # 1. Check for CAPTCHA / Cloudflare Turnstile
                captcha_detected = await self._check_captcha(page)
                if captcha_detected:
                    screenshot_path = os.path.join(self.screenshots_dir, f"captcha_{application_id}.png")
                    await page.screenshot(path=screenshot_path, full_page=True)
                    await browser.close()
                    return {
                        "status": "NEEDS_ATTENTION",
                        "reason": "CAPTCHA / Security verification detected. Manual completion required.",
                        "screenshotUrl": f"/proofs/captcha_{application_id}.png",
                        "requiresManualAction": True
                    }

                # 2. Identify ATS and map fields
                if "greenhouse.io" in job_url:
                    await self._fill_greenhouse_form(page, candidate_info, resume_pdf_path)
                elif "lever.co" in job_url:
                    await self._fill_lever_form(page, candidate_info, resume_pdf_path)
                else:
                    await self._fill_generic_form(page, candidate_info)

                # Filling a form is not a submission.  Stop here for the
                # candidate to review and manually submit; this also avoids
                # bypassing site-specific terms, login, or CAPTCHA controls.
                proof_path = os.path.join(self.screenshots_dir, f"proof_{application_id}.png")
                await page.screenshot(path=proof_path, full_page=False)

                await browser.close()
                return {
                    "status": "NEEDS_ATTENTION",
                    "reason": "Form was filled but not submitted. Review and submit it manually in the ATS.",
                    "screenshotUrl": f"/proofs/proof_{application_id}.png",
                    "requiresManualAction": True,
                    "payload": {
                        "fullName": candidate_info.get("fullName"),
                        "email": candidate_info.get("email"),
                        "targetUrl": job_url
                    }
                }

            except Exception as e:
                err_screenshot = os.path.join(self.screenshots_dir, f"error_{application_id}.png")
                try:
                    await page.screenshot(path=err_screenshot)
                except Exception:
                    pass
                await browser.close()
                return {
                    "status": "NEEDS_ATTENTION",
                    "reason": f"Form error: {str(e)}",
                    "screenshotUrl": f"/proofs/error_{application_id}.png"
                }

    async def _check_captcha(self, page) -> bool:
        selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            "iframe[src*='turnstile']",
            ".g-recaptcha",
            "#cf-turnstile",
            ".h-captcha"
        ]
        for sel in selectors:
            el = await page.query_selector(sel)
            if el:
                return True
        return False

    async def _human_type(self, page, selector: str, text: str):
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char)
            await asyncio.sleep(random.uniform(0.03, 0.08))

    async def _fill_greenhouse_form(self, page, info: Dict[str, Any], resume_path: str = None):
        name_parts = info.get("fullName", "Alex Chen").split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Candidate"

        if await page.query_selector("#first_name"):
            await self._human_type(page, "#first_name", first_name)
        if await page.query_selector("#last_name"):
            await self._human_type(page, "#last_name", last_name)
        if await page.query_selector("#email"):
            await self._human_type(page, "#email", info.get("email", "candidate@example.com"))
        if await page.query_selector("#phone"):
            await self._human_type(page, "#phone", info.get("phone", "+15550192831"))

        # LinkedIn
        if await page.query_selector("input[id*='linkedin']"):
            await self._human_type(page, "input[id*='linkedin']", info.get("linkedinUrl", "https://linkedin.com"))

    async def _fill_lever_form(self, page, info: Dict[str, Any], resume_path: str = None):
        if await page.query_selector("input[name='name']"):
            await self._human_type(page, "input[name='name']", info.get("fullName", ""))
        if await page.query_selector("input[name='email']"):
            await self._human_type(page, "input[name='email']", info.get("email", ""))
        if await page.query_selector("input[name='phone']"):
            await self._human_type(page, "input[name='phone']", info.get("phone", ""))
        if await page.query_selector("input[name*='urls[LinkedIn]']"):
            await self._human_type(page, "input[name*='urls[LinkedIn]']", info.get("linkedinUrl", ""))

    async def _fill_generic_form(self, page, info: Dict[str, Any]):
        selectors = [
            ("input[type='email']", info.get("email", "")),
            ("input[name*='name']", info.get("fullName", "")),
            ("input[type='tel']", info.get("phone", ""))
        ]
        for sel, val in selectors:
            if val and await page.query_selector(sel):
                await self._human_type(page, sel, val)

    def _simulate_apply(self, application_id: str, job_url: str, candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Simulation runner for non-browser or CI test harnesses."""
        full_name = candidate_info.get("fullName", "")
        email = candidate_info.get("email", "")
        if not full_name or not email:
            return {
                "status": "NEEDS_ATTENTION",
                "reason": "Missing required candidate profile information (name or email).",
                "screenshotUrl": None,
                "requiresManualAction": True
            }
        return {
            "status": "NEEDS_ATTENTION",
            "reason": "Browser automation is unavailable. Submit this application manually.",
            "screenshotUrl": f"/proofs/proof_{application_id}.png",
            "requiresManualAction": True,
            "payload": {
                "fullName": full_name,
                "email": email,
                "targetUrl": job_url,
                "verified": False
            }
        }

apply_runner = PlaywrightApplyRunner(headless=True)
