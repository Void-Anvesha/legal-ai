"""Judgment summarization service."""
from typing import List, Optional, Dict, Any
from loguru import logger

from ..models.case import CaseSummary, SummaryResponse
from ..core.config import settings
from ..core.exceptions import RAGError


class SummarizerService:
    """Service for summarizing legal judgments and documents."""

    async def summarize(self, text: str, document_id: str = "") -> SummaryResponse:
        """
        Generate comprehensive summary of a legal document.
        Uses LLM when available, falls back to extractive summarization.
        """
        if not text or len(text.strip()) == 0:
            raise RAGError("Empty text provided for summarization")

        # Try LLM-based summarization
        try:
            summary = await self._llm_summarize(text)
        except Exception as e:
            logger.warning(f"LLM summarization failed, using extractive method: {e}")
            summary = self._extractive_summarize(text)

        return SummaryResponse(
            document_id=document_id,
            short_summary=summary.short_summary,
            detailed_summary=summary.detailed_summary,
            key_findings=summary.key_findings,
            final_verdict=summary.final_verdict,
            legal_principles=summary.legal_principles,
        )

    async def _llm_summarize(self, text: str) -> CaseSummary:
        """Use LLM for abstractive summarization."""
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from ..prompts.summary_prompt import SummaryPromptBuilder

        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
            max_tokens=2000,
        )

        prompt_builder = SummaryPromptBuilder()

        # Generate short summary
        short_messages = [
            SystemMessage(content=prompt_builder.short_summary_system()),
            HumanMessage(content=prompt_builder.short_summary_user(text)),
        ]
        short_response = await llm.ainvoke(short_messages)
        short_summary = short_response.content

        # Generate detailed summary
        detailed_messages = [
            SystemMessage(content=prompt_builder.detailed_summary_system()),
            HumanMessage(content=prompt_builder.detailed_summary_user(text)),
        ]
        detailed_response = await llm.ainvoke(detailed_messages)
        detailed_summary = detailed_response.content

        # Extract key findings
        findings_messages = [
            SystemMessage(content=prompt_builder.key_findings_system()),
            HumanMessage(content=prompt_builder.key_findings_user(text)),
        ]
        findings_response = await llm.ainvoke(findings_messages)
        key_findings = self._parse_list(findings_response.content)

        # Extract final verdict
        verdict_messages = [
            SystemMessage(content=prompt_builder.verdict_system()),
            HumanMessage(content=prompt_builder.verdict_user(text)),
        ]
        verdict_response = await llm.ainvoke(verdict_messages)
        final_verdict = verdict_response.content

        # Extract legal principles
        principles_messages = [
            SystemMessage(content=prompt_builder.principles_system()),
            HumanMessage(content=prompt_builder.principles_user(text)),
        ]
        principles_response = await llm.ainvoke(principles_messages)
        legal_principles = self._parse_list(principles_response.content)

        return CaseSummary(
            short_summary=short_summary,
            detailed_summary=detailed_summary,
            key_findings=key_findings,
            final_verdict=final_verdict,
            legal_principles=legal_principles,
        )

    def _extractive_summarize(self, text: str) -> CaseSummary:
        """Fallback extractive summarization when LLM is unavailable."""
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]

        if not sentences:
            return CaseSummary(
                short_summary=text[:200],
                detailed_summary=text[:500],
                key_findings=["Unable to extract key findings"],
                final_verdict="Unable to determine verdict",
                legal_principles=[],
            )

        # Score sentences by importance
        scored_sentences = []
        important_keywords = [
            "held", "ordered", "decreed", "convicted", "acquitted", "sentenced",
            "appeal", "dismissed", "allowed", "directed", "observed", "conclusion",
            "finding", "verdict", "judgment", "principle", "ratio",
        ]

        for sentence in sentences:
            score = sum(1 for kw in important_keywords if kw.lower() in sentence.lower())
            scored_sentences.append((score, sentence))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        # Short summary: top 2-3 most important sentences
        short_summary = ". ".join([s for _, s in scored_sentences[:3]]) + "."

        # Detailed summary: top 8-10 sentences in original order
        top_indices = sorted(
            [sentences.index(s) for _, s in scored_sentences[:10]]
        )
        detailed_summary = ". ".join([sentences[i] for i in top_indices]) + "."

        # Key findings
        key_findings = [s for _, s in scored_sentences[:5] if len(s) > 30]

        # Final verdict
        verdict_sentences = [
            s for s in sentences
            if any(kw in s.lower() for kw in ["convicted", "acquitted", "dismissed", "allowed", "ordered"])
        ]
        final_verdict = verdict_sentences[0] if verdict_sentences else (
            "Verdict not clearly identified in the document."
        )

        # Legal principles
        principle_sentences = [
            s for s in sentences
            if any(kw in s.lower() for kw in ["principle", "ratio", "precedent", "laid down", "settled law"])
        ]
        legal_principles = principle_sentences[:5]

        return CaseSummary(
            short_summary=short_summary,
            detailed_summary=detailed_summary,
            key_findings=key_findings,
            final_verdict=final_verdict,
            legal_principles=legal_principles,
        )

    def _parse_list(self, text: str) -> List[str]:
        """Parse numbered/bulleted list from LLM response."""
        lines = text.strip().split("\n")
        items = []
        for line in lines:
            line = line.strip()
            # Remove numbering or bullets
            line = line.lstrip("0123456789.-) ")
            if line and len(line) > 5:
                items.append(line)
        return items[:10] if items else [text[:200]]


# Singleton
summarizer = SummarizerService()
