"""Legal document parser - extracts entities and metadata from legal text."""
import re
from typing import List, Optional, Dict, Any, Tuple
from loguru import logger

from ..models.document import (
    DocumentType,
    DocumentMetadata,
    ExtractedEntity,
)


class LegalParser:
    """Parse Indian legal documents to extract entities and metadata."""

    # Patterns for entity extraction
    CASE_NUMBER_PATTERNS = [
        r"(?:Crl\.?\s*(?:A|M\.?A|Rev|Pet)\.?\s*No\.?\s*[\d/]+(?:\s*of\s*\d{4})?)",
        r"(?:Civil\s*Appeal\s*No\.?\s*[\d/]+(?:\s*of\s*\d{4})?)",
        r"(?:Writ\s*Petition\s*(?:No\.?|C\.?)\s*[\d/]+(?:\s*of\s*\d{4})?)",
        r"(?:SLP\s*(?:C|Crl)\.?\s*No\.?\s*[\d/]+(?:\s*of\s*\d{4})?)",
        r"(?:FIR\s*No\.?\s*[\d/]+(?:\s*of\s*\d{4})?)",
        r"(?:Case\s*No\.?\s*[\d/]+(?:\s*of\s*\d{4})?)",
    ]

    DATE_PATTERNS = [
        r"\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}",
        r"\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
    ]

    COURT_PATTERNS = [
        r"(Supreme\s+Court\s+of\s+India)",
        r"(High\s+Court\s+of\s+\w+(?:\s+\w+)?)",
        r"(District\s+Court,?\s+\w+(?:\s+\w+)?)",
        r"(Sessions\s+Court,?\s+\w+(?:\s+\w+)?)",
        r"(Metropolitan\s+Magistrate,?\s+\w+(?:\s+\w+)?)",
    ]

    # Legal section patterns
    SECTION_PATTERNS = [
        # BNS sections
        r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)\s*(?:of\s+)?(?:the\s+)?(?:BNS|Bharatiya\s+Nyaya\s+Sanhita)",
        r"(?:BNS|Bharatiya\s+Nyaya\s+Sanhita)[,\s]+(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)",
        # IPC sections
        r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)\s*(?:of\s+)?(?:the\s+)?(?:IPC|Indian\s+Penal\s+Code)",
        r"(?:IPC|Indian\s+Penal\s+Code)[,\s]+(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)",
        # IT Act sections
        r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)\s*(?:of\s+)?(?:the\s+)?(?:IT\s+Act|Information\s+Technology\s+Act)",
        # BNSS sections
        r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)\s*(?:of\s+)?(?:the\s+)?(?:BNSS|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita)",
        # BSA sections
        r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)\s*(?:of\s+)?(?:the\s+)?(?:BSA|Bharatiya\s+Sakshya\s+Adhiniyam)",
        # Generic section reference
        r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)",
    ]

    # Crime category keywords
    CRIME_KEYWORDS = {
        "murder": ["murder", "killed", "homicide", "assassination", "culpable homicide"],
        "theft": ["theft", "stole", "stolen", "robbery", "dacoity", "looting"],
        "assault": ["assault", "battery", "hurt", "grievous hurt", "beating"],
        "fraud": ["fraud", "cheating", "forgery", "counterfeit", "misrepresentation", "scam"],
        "rape": ["rape", "sexual assault", "sexual harassment", "molestation", "outraging modesty"],
        "cybercrime": ["cyber", "hacking", "phishing", "identity theft", "online fraud", "data theft"],
        "corruption": ["corruption", "bribery", "bribe", "embezzlement", "misappropriation"],
        "kidnapping": ["kidnapping", "abduction", "hostage", "missing person"],
        "dowry": ["dowry", "dowry death", "cruelty by husband"],
        "defamation": ["defamation", "libel", "slander"],
        "drug_offense": ["narcotic", "drug", "psychotropic", "contraband"],
        "property_dispute": ["property", "land dispute", "encroachment", "trespass"],
        "constitutional": ["fundamental right", "constitutional", "writ", "mandamus", "habeas corpus"],
    }

    # Document type classification keywords
    DOC_TYPE_KEYWORDS = {
        DocumentType.COURT_JUDGMENT: [
            "judgment", "verdict", "convicted", "acquitted", "sentenced",
            "held that", "ordered", "decreed", "appeal is", "dismissed",
        ],
        DocumentType.FIR: [
            "first information report", "FIR", "fir no", "complainant",
            "accused", "offence registered", "police station",
        ],
        DocumentType.CHARGE_SHEET: [
            "charge sheet", "chargesheet", "charges framed",
            "offences charged", "prosecution evidence",
        ],
        DocumentType.PETITION: [
            "petition", "petitioner", "respondent", "prayer",
            "humble petition", "filed this petition",
        ],
        DocumentType.CONTRACT: [
            "agreement", "contract", "parties agree", "terms and conditions",
            "hereby agreed", "consideration", "obligations of",
        ],
        DocumentType.LEGAL_NOTICE: [
            "legal notice", "notice is hereby", "cease and desist",
            "demand notice", "you are hereby", "notice period",
        ],
        DocumentType.BAIL_APPLICATION: [
            "bail application", "bail", "release on bail",
            "bail bonds", "surety", "custody",
        ],
        DocumentType.WRIT_PETITION: [
            "writ petition", "article 32", "article 226",
            "mandamus", "certiorari", "prohibition", "quo warranto",
        ],
        DocumentType.APPEAL: [
            "appeal", "appellant", "impugned judgment",
            "challenged the order", "set aside",
        ],
    }

    def parse(self, text: str) -> Tuple[DocumentMetadata, List[ExtractedEntity], DocumentType]:
        """
        Parse a legal document and extract metadata, entities, and document type.

        Returns:
            Tuple of (metadata, entities, document_type)
        """
        if not text or len(text.strip()) == 0:
            return DocumentMetadata(), [], DocumentType.OTHER

        entities: List[ExtractedEntity] = []
        metadata = DocumentMetadata()

        # Extract case number
        case_number = self._extract_case_number(text)
        if case_number:
            metadata.case_number = case_number
            entities.append(ExtractedEntity(
                entity_type="case_number",
                value=case_number,
                confidence=0.95,
            ))

        # Extract court name
        court_name = self._extract_court(text)
        if court_name:
            metadata.court_name = court_name
            entities.append(ExtractedEntity(
                entity_type="court",
                value=court_name,
                confidence=0.9,
            ))

        # Extract dates
        dates = self._extract_dates(text)
        for date in dates[:5]:  # Limit to top 5 dates
            entities.append(ExtractedEntity(
                entity_type="date",
                value=date,
                confidence=0.85,
            ))
        if dates:
            metadata.date_of_judgment = dates[0]
            metadata.date_of_filing = dates[-1] if len(dates) > 1 else None

        # Extract parties
        parties = self._extract_parties(text)
        metadata.parties = parties
        for party in parties:
            entities.append(ExtractedEntity(
                entity_type="party",
                value=party,
                confidence=0.8,
            ))

        # Extract location
        location = self._extract_location(text)
        if location:
            metadata.location = location
            entities.append(ExtractedEntity(
                entity_type="location",
                value=location,
                confidence=0.75,
            ))

        # Extract crime category
        crime_category = self._extract_crime_category(text)
        if crime_category:
            metadata.crime_category = crime_category
            entities.append(ExtractedEntity(
                entity_type="crime",
                value=crime_category,
                confidence=0.85,
            ))

        # Extract evidence references
        evidence = self._extract_evidence(text)
        metadata.evidence_list = evidence
        for ev in evidence:
            entities.append(ExtractedEntity(
                entity_type="evidence",
                value=ev,
                confidence=0.7,
            ))

        # Extract legal keywords
        keywords = self._extract_keywords(text)
        metadata.keywords = keywords
        for kw in keywords[:10]:
            entities.append(ExtractedEntity(
                entity_type="keyword",
                value=kw,
                confidence=0.8,
            ))

        # Classify document type
        doc_type = self._classify_document_type(text)

        return metadata, entities, doc_type

    def _extract_case_number(self, text: str) -> Optional[str]:
        """Extract case number from text."""
        for pattern in self.CASE_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None

    def _extract_court(self, text: str) -> Optional[str]:
        """Extract court name from text."""
        for pattern in self.COURT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []
        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return list(dict.fromkeys(dates))[:5]  # Unique dates, max 5

    def _extract_parties(self, text: str) -> List[str]:
        """Extract party names from legal text."""
        parties = []

        # Pattern: "X vs Y" or "X v. Y" or "X versus Y"
        vs_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:vs?\.?|versus)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:Petitioner|Appellant|Plaintiff)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:Respondent|Defendant|Accused)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        for pattern in vs_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([m for m in match if m])
                else:
                    parties.append(match)

        # Clean and deduplicate
        cleaned = []
        for p in parties:
            p = p.strip()
            if len(p) > 2 and p not in cleaned:
                cleaned.append(p)

        return cleaned[:10]

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from legal text."""
        # Look for common location patterns
        location_patterns = [
            r"(?:at|in|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+)?)",
            r"(?:Police\s+Station\s*[-:]\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:District\s*[-:]\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_crime_category(self, text: str) -> Optional[str]:
        """Identify crime category from text."""
        text_lower = text.lower()
        category_scores: Dict[str, int] = {}

        for category, keywords in self.CRIME_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                category_scores[category] = score

        if category_scores:
            return max(category_scores, key=category_scores.get)
        return None

    def _extract_evidence(self, text: str) -> List[str]:
        """Extract evidence references from text."""
        evidence = []
        evidence_patterns = [
            r"(?:Exhibit|Ex\.?)\s*([PDC]\s*[-/]\s*\d+)",
            r"(?:document\s+marked\s+as\s+)(Ex\.?\s*\d+)",
            r"(?:DNA\s+(?:report|evidence|sample))",
            r"(?:CCTV\s+(?:footage|recording))",
            r"(?:Fingerprint\s+(?:report|evidence))",
            r"(?:Post[- ]mortem\s+report)",
            r"(?:Medical\s+(?:report|certificate|evidence))",
            r"(?:Witness\s+statement)",
            r"(?:Call\s+(?:detail|data)\s+records?)",
            r"(?:Electronic\s+evidence)",
        ]

        for pattern in evidence_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            evidence.extend(matches)

        return list(dict.fromkeys(evidence))[:10]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract legal keywords from text."""
        legal_terms = [
            "bail", "conviction", "acquittal", "appeal", "petition",
            "writ", "habeas corpus", "mandamus", "certiorari",
            "cognizable", "non-cognizable", "bailable", "non-bailable",
            "compoundable", "non-compoundable", "summary trial",
            "warrant case", "summons case", "anticipatory bail",
            "regular bail", "default bail", "quashing",
            "stay order", "injunction", "restraint order",
            "interim order", "final order", "judgment",
            "decree", "sentence", "punishment", "fine",
            "imprisonment", "life imprisonment", "death penalty",
            "probation", "parole", "remission",
            "restitution", "compensation", "damages",
            "mens rea", "actus reus", "guilty mind",
            "beyond reasonable doubt", "preponderance of evidence",
            "burden of proof", "presumption", "estoppel",
            "res judicata", "locus standi", "stare decisis",
            "ratio decidendi", "obiter dicta", "precedent",
        ]

        text_lower = text.lower()
        found = [term for term in legal_terms if term in text_lower]
        return found

    def _classify_document_type(self, text: str) -> DocumentType:
        """Classify the document type based on content."""
        text_lower = text.lower()
        type_scores: Dict[DocumentType, int] = {}

        for doc_type, keywords in self.DOC_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                type_scores[doc_type] = score

        if type_scores:
            return max(type_scores, key=type_scores.get)
        return DocumentType.OTHER


# Singleton
legal_parser = LegalParser()
