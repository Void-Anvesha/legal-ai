"""Fact extraction for victim complaint text."""
import json
import re
from typing import Any, Dict, List, Tuple

from loguru import logger

from ..core.config import settings
from ..models.intake import IncidentFacts, VictimProfile
from .case_classification_agent import case_classification_agent


class FactExtractionAgent:
    """Extract structured facts using LLM extraction with deterministic fallback."""

    allowed_categories = {
        "physical_assault",
        "theft_or_robbery",
        "cybercrime",
        "domestic_violence",
        "harassment_or_stalking",
        "fraud",
        "threat_or_intimidation",
        "property_dispute",
        "sexual_offence",
        "missing_person",
        "other_complaint",
    }

    evidence_keywords = ["photo", "video", "cctv", "recording", "screenshot", "document", "receipt", "फोटो", "वीडियो", "रिकॉर्डिंग", "स्क्रीनशॉट", "गवाह"]
    injury_keywords = ["injury", "injured", "bleeding", "fracture", "wound", "hospital", "hurt", "चोट", "घायल", "खून", "अस्पताल", "मारा", "पीटा", "मारपीट", "मारा-पीटा"]
    property_keywords = ["phone", "wallet", "money", "gold", "chain", "vehicle", "bike", "car", "property", "फोन", "पैसे", "सोना", "चेन", "गाड़ी", "बाइक"]
    threat_keywords = ["threat", "threatened", "blackmail", "kill", "harm", "warned", "धमकी", "ब्लैकमेल", "मारने"]
    digital_keywords = ["upi", "otp", "online", "account", "password", "hacked", "bank", "transaction", "यूपीआई", "ओटीपी", "ऑनलाइन", "अकाउंट", "बैंक"]

    def update_facts(self, existing: IncidentFacts, text: str) -> IncidentFacts:
        combined_description = self._append_unique(existing.description, text)
        facts = existing.model_copy(deep=True)
        facts.description = combined_description
        facts.type = case_classification_agent.classify(combined_description)
        facts.date = facts.date or self._extract_date(text)
        facts.time = facts.time or self._extract_time(text)
        facts.location = facts.location or self._extract_location(text)
        facts.sequence_of_events = self._append_list(facts.sequence_of_events, self._split_events(text))
        facts.accused = self._append_list(facts.accused, self._extract_people_after(text, ["accused", "suspect", "by"]))
        facts.witnesses = self._append_list(facts.witnesses, self._extract_people_after(text, ["witness", "saw by"]))
        facts.evidence = self._append_list(facts.evidence, self._extract_keyword_items(text, self.evidence_keywords))
        facts.injuries = self._append_list(facts.injuries, self._extract_keyword_items(text, self.injury_keywords))
        facts.property_loss = self._append_list(facts.property_loss, self._extract_keyword_items(text, self.property_keywords))
        facts.threats = self._append_list(facts.threats, self._extract_keyword_items(text, self.threat_keywords))
        facts.digital_elements = self._append_list(facts.digital_elements, self._extract_keyword_items(text, self.digital_keywords))
        facts.missing_information = self.missing_information(facts)
        return facts

    def update_case_details(
        self,
        existing_victim: VictimProfile,
        existing_facts: IncidentFacts,
        text: str,
        language: str = "en-IN",
        followup_key: str | None = None,
    ) -> Tuple[VictimProfile, IncidentFacts]:
        """Update victim and incident facts from English, Hindi, or Hinglish text."""
        victim = self.update_victim(existing_victim, text)
        facts = self.update_facts(existing_facts, text)

        if not self._llm_configured():
            facts = self.apply_followup_answer(facts, text, followup_key)
            facts = self._sanitize_facts(facts)
            return victim, facts

        try:
            extracted = self._llm_extract(victim, facts, text, language)
            victim = self._merge_victim(victim, extracted.get("victim", {}))
            facts = self._merge_facts(facts, extracted.get("incident", {}))
            extracted_category = extracted.get("complaint_category")
            if extracted_category in self.allowed_categories:
                facts.type = extracted_category
            else:
                facts.type = facts.type or case_classification_agent.classify(facts.description)
            facts.missing_information = self.missing_information(facts)
        except Exception as exc:
            logger.warning(f"LLM fact extraction failed; using deterministic fallback: {exc}")

        facts = self.apply_followup_answer(facts, text, followup_key)
        facts = self._sanitize_facts(facts)
        return victim, facts

    def apply_followup_answer(
        self,
        facts: IncidentFacts,
        answer: str,
        followup_key: str | None,
    ) -> IncidentFacts:
        """Treat direct answers to follow-up questions as the requested fact slot."""
        clean = answer.strip(" .,।")
        if not followup_key or not clean:
            return facts

        updated = facts.model_copy(deep=True)
        if followup_key == "incident description":
            updated.description = self._append_unique(updated.description, clean)
        elif followup_key == "incident date":
            if self._looks_like_date(clean):
                updated.date = updated.date or clean
        elif followup_key == "incident time":
            if self._looks_like_time(clean):
                updated.time = updated.time or clean
        elif followup_key == "incident location":
            if not self._is_low_information_answer(clean) and not self._looks_like_date(clean):
                updated.location = updated.location or clean
        elif followup_key == "accused or suspect details":
            if not self._is_affirmation(clean):
                value = self._unknown_label(clean, "Accused/suspect not known")
                updated.accused = self._append_list(updated.accused, [value])
        elif followup_key == "available evidence":
            if not self._is_affirmation(clean):
                value = self._unknown_label(clean, "No evidence available or stated")
                updated.evidence = self._append_list(updated.evidence, [value])

        updated.missing_information = self.missing_information(updated)
        return updated

    def _sanitize_facts(self, facts: IncidentFacts) -> IncidentFacts:
        """Remove or move obvious wrong-slot values before the UI renders them."""
        updated = facts.model_copy(deep=True)

        date_from_location = self._extract_date(updated.location or "")
        if updated.location and date_from_location and not self._looks_like_location(updated.location):
            if not self._looks_like_date(updated.date or ""):
                updated.date = updated.location
            updated.location = None

        date_from_time = self._extract_date(updated.time or "")
        if updated.time and date_from_time and not self._looks_like_time(updated.time):
            if not self._looks_like_date(updated.date or ""):
                updated.date = date_from_time
            updated.time = None

        if updated.date and not self._looks_like_date(updated.date):
            recovered_date = self._extract_date(updated.date)
            updated.date = recovered_date

        if updated.time and not self._looks_like_time(updated.time):
            recovered_time = self._extract_time(updated.time)
            updated.time = recovered_time

        if updated.location and not self._looks_like_location(updated.location):
            updated.location = None

        updated.missing_information = self.missing_information(updated)
        return updated

    def _is_affirmation(self, text: str) -> bool:
        return text.strip().lower() in {"yes", "yeah", "yep", "haan", "han", "ha", "हाँ", "हां", "जी", "जी हाँ", "जी हां"}

    def _is_low_information_answer(self, text: str) -> bool:
        clean = text.strip().lower()
        return self._is_affirmation(text) or clean in {"ok", "okay", "the incident", "incident", "घटना", "ठीक है"}

    def _looks_like_date(self, text: str | None) -> bool:
        if not text or self._is_low_information_answer(text):
            return False
        return bool(self._extract_date(text))

    def _looks_like_time(self, text: str | None) -> bool:
        if not text or self._is_low_information_answer(text):
            return False
        lowered = text.lower()
        if any(marker in lowered for marker in ["incident", "took", "happened", "घटना"]):
            return False
        return bool(self._extract_time(text))

    def _looks_like_location(self, text: str | None) -> bool:
        if not text or self._is_low_information_answer(text):
            return False
        if self._looks_like_date(text):
            return False
        lowered = text.lower()
        non_location_markers = [
            "don't know",
            "do not know",
            "didn't know",
            "did not know",
            "that person",
            "that man",
            "that woman",
            "he was",
            "she was",
            "they were",
            "accused",
            "suspect",
            "i was",
            "i am",
            "मुझे नहीं",
            "नहीं पता",
            "वह आदमी",
            "वह औरत",
        ]
        if any(marker in lowered for marker in non_location_markers):
            return False
        location_markers = [
            "near",
            "at",
            "in",
            "outside",
            "road",
            "street",
            "market",
            "home",
            "house",
            "office",
            "school",
            "college",
            "station",
            "पास",
            "में",
            "बाहर",
            "घर",
            "बाजार",
            "सड़क",
            "थाना",
            "ऑफिस",
            "स्कूल",
            "कॉलेज",
        ]
        if any(marker in lowered for marker in location_markers):
            return True

        indian_places = {
            "bhopal",
            "delhi",
            "new delhi",
            "mumbai",
            "kolkata",
            "chennai",
            "bengaluru",
            "bangalore",
            "hyderabad",
            "pune",
            "jaipur",
            "lucknow",
            "indore",
            "patna",
            "kanpur",
            "nagpur",
            "gwalior",
            "agra",
            "varanasi",
        }
        if lowered.strip(" .,") in indian_places:
            return True

        words = text.strip(" .,").split()
        if 1 <= len(words) <= 4 and not re.search(r"\b(?:i|he|she|they|we|was|were|am|is|are|know|happened|stabbed|hit|stole)\b", lowered):
            return any(word[:1].isupper() for word in words)

        return False

    def _unknown_label(self, text: str, fallback: str) -> str:
        lowered = text.lower()
        unknown_markers = {
            "no",
            "none",
            "unknown",
            "not known",
            "do not know",
            "don't know",
            "nahi",
            "nahin",
            "nahi pata",
            "nahin pata",
            "नहीं",
            "नही",
            "नहीं पता",
            "पता नहीं",
            "कोई नहीं",
        }
        return fallback if lowered in unknown_markers or any(marker in lowered for marker in unknown_markers) else text

    def update_victim(self, existing: VictimProfile, text: str) -> VictimProfile:
        """Extract complainant details only when the victim states them directly."""
        victim = existing.model_copy(deep=True)
        victim.name = victim.name or self._extract_named_value(
            text,
            [
                r"\bmy name is\s+([A-Z][A-Za-z\s.]{2,60}?)(?=\.|,|$|\s+(?:and|i|my))",
                r"\bi am\s+([A-Z][A-Za-z\s.]{2,60}?)(?=\.|,|$|\s+(?:and|my))",
            ],
        )
        victim.age = victim.age or self._first_match(
            [
                r"\b\d{1,3}\s*(?:years old|year old|yrs old)\b",
                r"\bage\s*(?:is|:)?\s*\d{1,3}\b",
            ],
            text,
        )
        victim.contact = victim.contact or self._first_match(
            [r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"],
            text,
        )
        victim.address = victim.address or self._extract_named_value(
            text,
            [
                r"\b(?:my address is|i live at|i live in)\s+([A-Za-z0-9\s,.-]{5,90})",
            ],
        )
        return victim

    def _llm_extract(
        self,
        victim: VictimProfile,
        facts: IncidentFacts,
        latest_text: str,
        language: str,
    ) -> Dict[str, Any]:
        """Use an LLM to understand Hindi, Hinglish, and English complaint text."""
        system_prompt = (
            "You are a police complaint fact extraction engine for BolnaAI in India. "
            "You understand Hindi, Hinglish, English, and mixed speech transcripts. "
            "Extract only facts explicitly stated by the complainant. Do not infer, assume, accuse, "
            "or add legal conclusions. Return only valid JSON. Preserve names, places, dates, and "
            "phrases in the language/script used by the complainant when possible. "
            "If a field is unknown, return null or an empty list. "
            "For complaint_category, choose one of: physical_assault, theft_or_robbery, cybercrime, "
            "domestic_violence, harassment_or_stalking, fraud, threat_or_intimidation, "
            "property_dispute, sexual_offence, missing_person, other_complaint."
        )
        user_payload = {
            "selected_language": language,
            "latest_transcript": latest_text,
            "existing_victim": victim.model_dump(),
            "existing_incident": facts.model_dump(),
            "required_json_shape": {
                "victim": {
                    "name": "string or null",
                    "age": "string or null",
                    "gender": "string or null",
                    "contact": "string or null",
                    "address": "string or null",
                },
                "complaint_category": "one allowed category string",
                "incident": {
                    "date": "string or null",
                    "time": "string or null",
                    "location": "string or null",
                    "description": "combined factual complaint narrative",
                    "sequence_of_events": ["short event strings"],
                    "accused": ["accused/suspect details explicitly stated"],
                    "witnesses": ["witness details explicitly stated"],
                    "evidence": ["evidence explicitly stated"],
                    "injuries": ["injury details explicitly stated"],
                    "property_loss": ["property/loss details explicitly stated"],
                    "threats": ["threat details explicitly stated"],
                    "digital_elements": ["digital/cyber/payment details explicitly stated"],
                },
            },
            "extraction_rules": [
                "Treat Hindi relative dates such as आज, कल, परसों, कल रात as date/time facts.",
                "Treat Hindi place phrases such as घर के पास, बाजार में, थाना, सड़क, ऑफिस as location facts.",
                "Treat मारपीट, मारा, पीटा, चोट, खून, अस्पताल as injury/assault-related facts.",
                "Do not mark a missing field as present unless the transcript explicitly states it.",
                "Keep the output concise and structured for a police officer review draft.",
            ],
        }
        provider = settings.LLM_PROVIDER.strip().lower()
        if provider == "gemini":
            return self._gemini_extract(system_prompt, user_payload)
        if provider == "openai":
            return self._openai_extract(system_prompt, user_payload)
        raise ValueError(f"Unsupported LLM provider for fact extraction: {settings.LLM_PROVIDER}")

    def _llm_configured(self) -> bool:
        provider = settings.LLM_PROVIDER.strip().lower()
        if provider == "gemini":
            return bool(settings.GEMINI_API_KEY)
        if provider == "openai":
            return bool(settings.OPENAI_API_KEY)
        return False

    def _gemini_extract(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=json.dumps(user_payload, ensure_ascii=False),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                response_mime_type="application/json",
            ),
        )
        content = response.text or "{}"
        return json.loads(content)

    def _openai_extract(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def _merge_victim(self, victim: VictimProfile, extracted: Dict[str, Any]) -> VictimProfile:
        updated = victim.model_copy(deep=True)
        for field in ["name", "age", "gender", "contact", "address"]:
            value = self._clean_scalar(extracted.get(field))
            if value and not getattr(updated, field):
                setattr(updated, field, value)
        return updated

    def _merge_facts(self, facts: IncidentFacts, extracted: Dict[str, Any]) -> IncidentFacts:
        updated = facts.model_copy(deep=True)
        for field in ["date", "time", "location"]:
            value = self._clean_scalar(extracted.get(field))
            if value and not getattr(updated, field):
                setattr(updated, field, value)

        description = self._clean_scalar(extracted.get("description"))
        if description:
            updated.description = self._append_unique(updated.description, description)

        for field in [
            "sequence_of_events",
            "accused",
            "witnesses",
            "evidence",
            "injuries",
            "property_loss",
            "threats",
            "digital_elements",
        ]:
            values = self._clean_list(extracted.get(field))
            setattr(updated, field, self._append_list(getattr(updated, field), values))

        return updated

    def _clean_scalar(self, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        clean = value.strip()
        if not clean or clean.lower() in {"null", "none", "unknown", "not specified", "नहीं पता"}:
            return None
        return clean

    def _clean_list(self, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    def missing_information(self, facts: IncidentFacts) -> List[str]:
        missing = []
        if len(facts.description.strip()) < 30:
            missing.append("incident description")
        if not facts.date:
            missing.append("incident date")
        if not facts.time:
            missing.append("incident time")
        if not facts.location:
            missing.append("incident location")
        if not facts.accused:
            missing.append("accused or suspect details")
        if not facts.evidence:
            missing.append("available evidence")
        return missing

    def is_complete_enough(self, facts: IncidentFacts) -> bool:
        required = {"incident description", "incident location"}
        missing = set(facts.missing_information)
        return not required.intersection(missing) and len(facts.description.strip()) >= 80

    def _append_unique(self, original: str, addition: str) -> str:
        clean = addition.strip()
        if not clean:
            return original
        if clean.lower() in original.lower():
            return original
        return f"{original}\n{clean}".strip()

    def _append_list(self, original: List[str], additions: List[str]) -> List[str]:
        seen = {item.lower() for item in original}
        merged = list(original)
        for item in additions:
            clean = item.strip(" .,")
            if clean and clean.lower() not in seen:
                merged.append(clean)
                seen.add(clean.lower())
        return merged

    def _extract_date(self, text: str) -> str | None:
        patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{1,2}[/-]\d{1,2}\b",
            r"\b(?:today|yesterday|last night|this morning|this evening)\b",
            r"\b\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{2,4}\b",
            r"(?:आज|कल|परसों|बीती रात|पिछली रात|आज सुबह|आज शाम|कल रात)",
            r"\d{1,2}\s*(?:तारीख|दिनांक)",
            r"\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4}\b",
        ]
        return self._first_match(patterns, text)

    def _extract_time(self, text: str) -> str | None:
        patterns = [
            r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",
            r"\b\d{1,2}\s*(?:am|pm)\b",
            r"\b(?:morning|afternoon|evening|night|midnight)\b",
            r"(?:सुबह|दोपहर|शाम|रात|आधी रात)",
        ]
        return self._first_match(patterns, text)

    def _extract_location(self, text: str) -> str | None:
        match = re.search(
            r"\b(?:at|near|in|outside)\s+([A-Z][\w\s,.-]{2,80}?)"
            r"(?=\s+(?:at|around|on|when|while|and|the accused|he|she|they|"
            r"[A-Z][a-z]+\s+(?:hit|threatened|stole|snatched|robbed|attacked))|[.,]|$)",
            text,
        )
        if match:
            return match.group(1).strip(" .,")
        lowered = text.lower()
        for marker in ["police station", "market", "home", "office", "school", "college", "road", "थाना", "बाजार", "घर", "ऑफिस", "स्कूल", "कॉलेज", "सड़क"]:
            if marker in lowered:
                return marker
        return None

    def _extract_people_after(self, text: str, markers: List[str]) -> List[str]:
        people = []
        for marker in markers:
            pattern = rf"\b{re.escape(marker)}\s+(?:is|was|named|called)?\s*([A-Z][A-Za-z\s.]{2,40})"
            people.extend(match.strip() for match in re.findall(pattern, text))
        return people

    def _extract_named_value(self, text: str, patterns: List[str]) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip(" .,")
        return None

    def _extract_keyword_items(self, text: str, keywords: List[str]) -> List[str]:
        lowered = text.lower()
        return [keyword for keyword in keywords if keyword in lowered]

    def _split_events(self, text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [sentence[:240] for sentence in sentences if len(sentence.strip()) > 20]

    def _first_match(self, patterns: List[str], text: str) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None


fact_extraction_agent = FactExtractionAgent()
