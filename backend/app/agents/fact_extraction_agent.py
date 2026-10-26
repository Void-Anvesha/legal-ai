"""Fact extraction for victim complaint text."""
import re
from typing import List

from ..models.intake import IncidentFacts, VictimProfile
from .case_classification_agent import case_classification_agent


class FactExtractionAgent:
    """Extract structured facts using deterministic, inspectable rules."""

    evidence_keywords = ["photo", "video", "cctv", "recording", "screenshot", "document", "receipt"]
    injury_keywords = ["injury", "injured", "bleeding", "fracture", "wound", "hospital", "hurt"]
    property_keywords = ["phone", "wallet", "money", "gold", "chain", "vehicle", "bike", "car", "property"]
    threat_keywords = ["threat", "threatened", "blackmail", "kill", "harm", "warned"]
    digital_keywords = ["upi", "otp", "online", "account", "password", "hacked", "bank", "transaction"]

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
            r"\b(?:today|yesterday|last night|this morning|this evening)\b",
            r"\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4}\b",
        ]
        return self._first_match(patterns, text)

    def _extract_time(self, text: str) -> str | None:
        patterns = [
            r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",
            r"\b\d{1,2}\s*(?:am|pm)\b",
            r"\b(?:morning|afternoon|evening|night|midnight)\b",
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
        for marker in ["police station", "market", "home", "office", "school", "college", "road"]:
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
