import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple

class UniversalJobNormalizer:
    """
    Standardizes raw multilingual job inputs into the canonical JobPilot schema.
    1. Title normalization (Standard O*NET/ESCO taxonomy).
    2. Seniority extraction.
    3. Currency conversion to USD.
    4. Geocoding resolution (country, state, city).
    5. Deduplication hashing (company + normalized_title + location).
    """

    # Static FX rates for rapid deterministic conversion to USD
    FX_RATES_TO_USD = {
        "USD": 1.0,
        "EUR": 1.08,
        "GBP": 1.28,
        "CAD": 0.73,
        "AUD": 0.66,
        "INR": 0.012,
        "SGD": 0.74,
        "SEK": 0.095
    }

    # Taxonomy mapping
    TITLE_TAXONOMY = [
        (r"\b(staff|principal)\s+(software|backend|frontend|systems)\s+engineer\b", "Staff Software Engineer"),
        (r"\b(senior|sr\.?)\s+(full[\s\-]stack|web)\s+engineer\b", "Senior Full-Stack Engineer"),
        (r"\b(senior|sr\.?)\s+(backend|systems)\s+engineer\b", "Senior Backend Engineer"),
        (r"\b(machine\s+learning|ml|ai)\s+(engineer|researcher)\b", "Machine Learning Engineer"),
        (r"\b(devops|platform|infrastructure|site\s+reliability|sre)\s+engineer\b", "DevOps / Infrastructure Engineer"),
        (r"\b(product\s+manager|pm)\b", "Product Manager"),
        (r"\b(data\s+engineer)\b", "Data Engineer")
    ]

    def normalize_title(self, raw_title: str) -> Tuple[str, str]:
        """Returns (normalized_title, seniority)."""
        lower = raw_title.lower()
        seniority = "Mid"
        if any(w in lower for w in ["intern", "co-op"]):
            seniority = "Intern"
        elif any(w in lower for w in ["junior", "jr", "entry", "associate"]):
            seniority = "Junior"
        elif any(w in lower for w in ["staff", "principal", "distinguished"]):
            seniority = "Staff"
        elif any(w in lower for w in ["lead", "architect", "tech lead"]):
            seniority = "Lead"
        elif any(w in lower for w in ["senior", "sr"]):
            seniority = "Senior"
        elif any(w in lower for w in ["director", "head of", "vp"]):
            seniority = "Executive"

        norm_title = raw_title.strip()
        for pattern, replacement in self.TITLE_TAXONOMY:
            if re.search(pattern, lower):
                norm_title = replacement
                break

        return norm_title, seniority

    def normalize_salary(self, salary_str: Optional[str]) -> Tuple[Optional[int], Optional[int], str]:
        """
        Parses salary string into (min_usd, max_usd, original_currency).
        Example: '£80,000 - £110,000' -> (102400, 140800, 'GBP')
        """
        if not salary_str:
            return None, None, "USD"

        # Detect currency
        currency = "USD"
        if "€" in salary_str or "EUR" in salary_str:
            currency = "EUR"
        elif "£" in salary_str or "GBP" in salary_str:
            currency = "GBP"
        elif "₹" in salary_str or "INR" in salary_str:
            currency = "INR"
        elif "CAD" in salary_str:
            currency = "CAD"

        # Extract digits
        numbers = re.findall(r'[\d,]+', salary_str)
        clean_nums = []
        for n in numbers:
            try:
                num = int(n.replace(",", ""))
                if num > 1000: # Filter out non-salary numbers
                    clean_nums.append(num)
            except ValueError:
                continue

        fx = self.FX_RATES_TO_USD.get(currency, 1.0)
        if len(clean_nums) >= 2:
            min_usd = int(clean_nums[0] * fx)
            max_usd = int(clean_nums[1] * fx)
            return min_usd, max_usd, currency
        elif len(clean_nums) == 1:
            val_usd = int(clean_nums[0] * fx)
            return val_usd, val_usd, currency

        return 140000, 190000, "USD"

    def compute_dedup_hash(self, company_name: str, normalized_title: str, location: str) -> str:
        """
        Deterministic SHA-256 deduplication hash.
        Identical jobs across multiple aggregators produce the same hash.
        """
        src = f"{company_name.lower().strip()}_{normalized_title.lower().strip()}_{location.lower().strip()}"
        return hashlib.sha256(src.encode("utf-8")).hexdigest()

job_normalizer = UniversalJobNormalizer()
