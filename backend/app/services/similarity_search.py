"""Similarity search service for finding similar legal cases."""
from typing import List, Dict, Any, Optional
from loguru import logger

from ..models.case import SimilarCase, CaseOutcome, SimilarCaseResponse
from ..database.vector_store import vector_store
from ..services.embeddings import EmbeddingService
from ..core.config import settings
from ..core.exceptions import RAGError


# Landmark case database for similarity matching
LANDMARK_CASES: List[Dict[str, Any]] = [
    {
        "id": "sc_001",
        "case_title": "Bachan Singh v. State of Punjab",
        "case_number": "AIR 1980 SC 898",
        "court": "Supreme Court of India",
        "date": "1980-09-09",
        "acts_sections": ["IPC 302", "IPC 354(3) CrPC"],
        "brief_facts": "The constitutionality of the death penalty was challenged. The court upheld the death penalty but restricted it to the rarest of rare cases.",
        "outcome": "convicted",
        "key_holdings": [
            "Death penalty is constitutional but should be used in rarest of rare cases",
            "Life imprisonment is the rule, death penalty is the exception",
            "Mitigating circumstances must be weighed against aggravating circumstances",
        ],
    },
    {
        "id": "sc_002",
        "case_title": "Vishaka v. State of Rajasthan",
        "case_number": "AIR 1997 SC 3011",
        "court": "Supreme Court of India",
        "date": "1997-08-13",
        "acts_sections": ["IPC 354", "IPC 376"],
        "brief_facts": "Landmark case on sexual harassment at workplace. The court laid down Vishaka Guidelines for prevention of sexual harassment.",
        "outcome": "convicted",
        "key_holdings": [
            "Employers must provide safe working environment for women",
            "Vishaka Guidelines established for prevention of sexual harassment",
            "Laid foundation for the Sexual Harassment of Women at Workplace Act, 2013",
        ],
    },
    {
        "id": "sc_003",
        "case_title": "Shreya Singhal v. Union of India",
        "case_number": "AIR 2015 SC 1523",
        "court": "Supreme Court of India",
        "date": "2015-03-24",
        "acts_sections": ["IT Act 66A", "IT Act 69", "IT Act 79"],
        "brief_facts": "Constitutionality of Section 66A of IT Act was challenged. The court struck down the section as unconstitutional.",
        "outcome": "acquitted",
        "key_holdings": [
            "Section 66A IT Act struck down as unconstitutional — violates Article 19(1)(a)",
            "Distinction between discussion, advocacy, and incitement",
            "Online speech enjoys same constitutional protection as offline speech",
        ],
    },
    {
        "id": "sc_004",
        "case_title": "Mathura Rape Case — Tukaram v. State of Maharashtra",
        "case_number": "AIR 1979 SC 185",
        "court": "Supreme Court of India",
        "date": "1979-01-01",
        "acts_sections": ["IPC 376", "IPC 354"],
        "brief_facts": "Young tribal girl raped in police station. The acquittal by SC led to nationwide protests and eventual legal reforms on consent in rape law.",
        "outcome": "acquitted",
        "key_holdings": [
            "Absence of injury does not imply consent",
            "Led to amendments in rape law",
            "Highlighted institutional violence against women",
        ],
    },
    {
        "id": "sc_005",
        "case_title": "Machhi Singh v. State of Punjab",
        "case_number": "AIR 1983 SC 957",
        "court": "Supreme Court of India",
        "date": "1983-01-01",
        "acts_sections": ["IPC 302"],
        "brief_facts": "Guidelines laid down for when death penalty should be imposed — rarest of rare cases test elaborated.",
        "outcome": "convicted",
        "key_holdings": [
            "Elaborated the 'rarest of rare' doctrine",
            "Five categories identified for death penalty consideration",
            "Manner of commission, motive, anti-social nature, magnitude of crime",
        ],
    },
    {
        "id": "sc_006",
        "case_title": "Nirbhaya Case — Mukesh v. State of NCT of Delhi",
        "case_number": "AIR 2017 SC 1901",
        "court": "Supreme Court of India",
        "date": "2017-05-05",
        "acts_sections": ["IPC 302", "IPC 376", "IPC 376A", "IPC 376D"],
        "brief_facts": "Gang rape and murder case that shocked the nation. Led to criminal law amendments in 2013.",
        "outcome": "convicted",
        "key_holdings": [
            "Death penalty confirmed for brutal rape and murder",
            "Led to Criminal Law Amendment Act 2013",
            "New offences added: stalking, voyeurism, acid attack",
            "Death penalty introduced for repeat rape offenders",
        ],
    },
    {
        "id": "sc_007",
        "case_title": "Kesavananda Bharati v. State of Kerala",
        "case_number": "AIR 1973 SC 1461",
        "court": "Supreme Court of India",
        "date": "1973-04-24",
        "acts_sections": ["Constitution of India", "Article 368", "Article 31"],
        "brief_facts": "Landmark case establishing the basic structure doctrine — Parliament cannot alter the basic structure of the Constitution.",
        "outcome": "appeal_allowed",
        "key_holdings": [
            "Basic structure doctrine established",
            "Parliament has wide powers of amendment but not unlimited",
            "Judicial review is part of basic structure",
            "Federalism, secularism, democracy are basic features",
        ],
    },
    {
        "id": "sc_008",
        "case_title": "Arnesh Kumar v. State of Bihar",
        "case_number": "AIR 2014 SC 2756",
        "court": "Supreme Court of India",
        "date": "2014-07-02",
        "acts_sections": ["IPC 498A", "CrPC 41", "CrPC 41A"],
        "brief_facts": "Guidelines issued to prevent misuse of Section 498A IPC. Police must follow procedure before arrest.",
        "outcome": "appeal_allowed",
        "key_holdings": [
            "Arrest not automatic in Section 498A cases",
            "Police must satisfy necessity of arrest under Section 41 CrPC",
            "Checklist to be followed before arrest",
            "Family members should not be routinely arrested",
        ],
    },
    {
        "id": "hc_001",
        "case_title": "State of Maharashtra v. Rajan (Cyber Fraud)",
        "case_number": "2023 Bom CR 456",
        "court": "Bombay High Court",
        "date": "2023-03-15",
        "acts_sections": ["IT Act 66", "IT Act 66C", "IT Act 66D", "IPC 420"],
        "brief_facts": "Online banking fraud involving identity theft and phishing. Accused convicted under IT Act and IPC.",
        "outcome": "convicted",
        "key_holdings": [
            "Digital evidence is admissible under Indian Evidence Act Section 65B",
            "IP address logs constitute valid electronic evidence",
            "Combined charges under IT Act and IPC permissible",
        ],
    },
    {
        "id": "hc_002",
        "case_title": "Delhi Domestic Violence Case",
        "case_number": "2022 Del HC 789",
        "court": "Delhi High Court",
        "date": "2022-07-20",
        "acts_sections": ["IPC 498A", "IPC 304B", "Domestic Violence Act 2005"],
        "brief_facts": "Cruelty and harassment for dowry leading to death. Multiple accused convicted under 498A and 304B.",
        "outcome": "convicted",
        "key_holdings": [
            "Cruelty need not be physical — mental cruelty sufficient",
            "Dowry death presumption under 304B applies",
            "Living separately does not negate cruelty allegations",
        ],
    },
    {
        "id": "sc_009",
        "case_title": "Justice K.S. Puttaswamy v. Union of India",
        "case_number": "AIR 2017 SC 4161",
        "court": "Supreme Court of India",
        "date": "2017-08-24",
        "acts_sections": ["Constitution Article 21", "IT Act 43A", "IT Act 66A"],
        "brief_facts": "Right to privacy declared as fundamental right under Article 21.",
        "outcome": "appeal_allowed",
        "key_holdings": [
            "Right to privacy is a fundamental right",
            "Part of Article 21 — right to life and personal liberty",
            "Data protection requires robust legal framework",
            "State must justify any privacy intrusion",
        ],
    },
    {
        "id": "sc_010",
        "case_title": "Navtej Singh Johar v. Union of India",
        "case_number": "AIR 2018 SC 4321",
        "court": "Supreme Court of India",
        "date": "2018-09-06",
        "acts_sections": ["IPC 377", "Constitution Article 14", "Article 21"],
        "brief_facts": "Section 377 IPC partially struck down — consensual homosexual acts decriminalized.",
        "outcome": "appeal_allowed",
        "key_holdings": [
            "Section 377 unconstitutional as applied to consensual acts",
            "Right to privacy includes sexual autonomy",
            "Equality and non-discrimination are fundamental",
            "Dignity and autonomy of individuals protected",
        ],
    },
    {
        "id": "hc_003",
        "case_title": "State of Karnataka v. Shivakumar (Dacoity)",
        "case_number": "2021 Kar HC 234",
        "court": "Karnataka High Court",
        "date": "2021-11-10",
        "acts_sections": ["IPC 395", "IPC 397", "IPC 34"],
        "brief_facts": "Five persons convicted for dacoity with weapons in a residential area.",
        "outcome": "convicted",
        "key_holdings": [
            "Common intention established through coordinated attack",
            "Presence of weapons enhances the offence to dacoity",
            "Each member liable for acts of all in furtherance of common intention",
        ],
    },
    {
        "id": "hc_004",
        "case_title": "R v. Mehta (Cheating and Fraud)",
        "case_number": "2020 Guj HC 567",
        "court": "Gujarat High Court",
        "date": "2020-06-15",
        "acts_sections": ["IPC 420", "IPC 406", "IPC 120B"],
        "brief_facts": "Financial fraud involving multiple victims. Accused convicted of criminal conspiracy and cheating.",
        "outcome": "convicted",
        "key_holdings": [
            "Criminal conspiracy established through coordinated actions",
            "Cheating proved by false representation inducing delivery of property",
            "Criminal breach of trust — misappropriation of entrusted funds",
        ],
    },
    {
        "id": "sc_011",
        "case_title": "DK Basu v. State of West Bengal",
        "case_number": "AIR 1997 SC 610",
        "court": "Supreme Court of India",
        "date": "1997-07-11",
        "acts_sections": ["Constitution Article 21", "Article 22", "CrPC 41"],
        "brief_facts": "Guidelines laid down for arrest and detention procedures to prevent custodial violence.",
        "outcome": "appeal_allowed",
        "key_holdings": [
            "Detailed guidelines for arrest procedure",
            "Police must identify themselves and prepare memo",
            "Right to inform relative/friend about arrest",
            "Medical examination must be conducted",
            "Violation of guidelines renders officials liable",
        ],
    },
    {
        "id": "sc_012",
        "case_title": "Lalita Kumari v. Government of UP",
        "case_number": "AIR 2014 SC 187",
        "court": "Supreme Court of India",
        "date": "2014-01-01",
        "acts_sections": ["CrPC 154", "IPC 302"],
        "brief_facts": "Mandatory registration of FIR for cognizable offences. Police cannot refuse to register FIR.",
        "outcome": "appeal_allowed",
        "key_holdings": [
            "Registration of FIR is mandatory for cognizable offences",
            "Police cannot conduct preliminary inquiry before registering FIR",
            "Preliminary inquiry allowed only in exceptional cases",
            "Delay in FIR registration must be explained",
        ],
    },
]


class SimilaritySearchService:
    """Service for finding similar legal cases."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self._cases_indexed = False

    async def find_similar_cases(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> SimilarCaseResponse:
        """Find cases similar to the given query."""
        await self._ensure_cases_indexed()

        # Search in vector store
        search_results = await vector_store.search(
            query=query,
            top_k=top_k,
            min_similarity=min_similarity,
            collection_name="landmark_cases",
        )

        # If no results from vector store, use keyword matching fallback
        if not search_results:
            return self._keyword_search(query, top_k)

        similar_cases = []
        for result in search_results:
            meta = result.get("metadata", {})
            case = SimilarCase(
                id=meta.get("id", ""),
                case_title=meta.get("case_title", "Unknown"),
                case_number=meta.get("case_number"),
                court=meta.get("court", "Unknown Court"),
                date=meta.get("date"),
                acts_sections=meta.get("acts_sections", []),
                brief_facts=result.get("text", ""),
                outcome=CaseOutcome(meta.get("outcome", "pending")),
                key_holdings=meta.get("key_holdings", []),
                similarity_score=result["similarity_score"],
            )
            similar_cases.append(case)

        # Sort by similarity
        similar_cases.sort(key=lambda x: x.similarity_score, reverse=True)

        return SimilarCaseResponse(
            query=query,
            similar_cases=similar_cases[:top_k],
            total_results=len(similar_cases),
        )

    async def _ensure_cases_indexed(self):
        """Ensure landmark cases are indexed in the vector store."""
        if self._cases_indexed:
            return

        try:
            count = vector_store.get_collection_count("landmark_cases") if hasattr(vector_store, 'get_collection_count') else 0
            if count > 0:
                self._cases_indexed = True
                return
        except Exception:
            pass

        # Index landmark cases
        from ..database.chroma_db import chroma_manager

        collection = chroma_manager.get_collection("landmark_cases")
        if collection.count() > 0:
            self._cases_indexed = True
            return

        texts = []
        metadatas = []
        ids = []

        for case in LANDMARK_CASES:
            case_text = (
                f"Case: {case['case_title']}\n"
                f"Court: {case['court']}\n"
                f"Date: {case.get('date', 'N/A')}\n"
                f"Sections: {', '.join(case['acts_sections'])}\n"
                f"Facts: {case['brief_facts']}\n"
                f"Holdings: {'; '.join(case['key_holdings'])}\n"
                f"Outcome: {case['outcome']}"
            )
            texts.append(case_text)
            metadatas.append({
                "id": case["id"],
                "case_title": case["case_title"],
                "case_number": case.get("case_number", ""),
                "court": case["court"],
                "date": case.get("date", ""),
                "acts_sections": case["acts_sections"],
                "outcome": case["outcome"],
                "key_holdings": case["key_holdings"],
            })
            ids.append(case["id"])

        # Generate embeddings
        embeddings = await self.embedding_service.embed_texts(texts)

        chroma_manager.add_documents(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            collection_name="landmark_cases",
        )

        self._cases_indexed = True
        logger.info(f"Indexed {len(LANDMARK_CASES)} landmark cases")

    def _keyword_search(self, query: str, top_k: int) -> SimilarCaseResponse:
        """Fallback keyword-based search when vector search unavailable."""
        query_lower = query.lower()
        scored_cases = []

        for case in LANDMARK_CASES:
            case_text = (
                f"{case['case_title']} {case['brief_facts']} "
                f"{' '.join(case['key_holdings'])} {' '.join(case['acts_sections'])}"
            ).lower()

            # Simple keyword overlap scoring
            query_words = set(query_lower.split())
            case_words = set(case_text.split())
            overlap = len(query_words & case_words)

            if overlap > 0:
                similarity = min(0.95, overlap / max(len(query_words), 1))
                scored_cases.append((similarity, case))

        scored_cases.sort(key=lambda x: x[0], reverse=True)

        similar_cases = []
        for similarity, case in scored_cases[:top_k]:
            similar_cases.append(SimilarCase(
                id=case["id"],
                case_title=case["case_title"],
                case_number=case.get("case_number"),
                court=case["court"],
                date=case.get("date"),
                acts_sections=case["acts_sections"],
                brief_facts=case["brief_facts"],
                outcome=CaseOutcome(case["outcome"]),
                key_holdings=case["key_holdings"],
                similarity_score=round(similarity, 4),
            ))

        return SimilarCaseResponse(
            query=query,
            similar_cases=similar_cases,
            total_results=len(similar_cases),
        )


# Singleton
similarity_search = SimilaritySearchService()
