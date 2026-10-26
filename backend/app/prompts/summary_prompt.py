"""Prompt templates for legal document summarization."""


class SummaryPromptBuilder:
    """Builds prompts for different types of legal summaries."""

    def short_summary_system(self) -> str:
        return (
            "You are an expert Indian legal analyst. Your task is to generate a concise "
            "2-3 sentence summary of a legal document. Focus on the core issue, the court's "
            "decision, and the key outcome. Use clear, professional language. "
            "Do not add any information not present in the document."
        )

    def short_summary_user(self, text: str) -> str:
        return (
            f"Provide a brief 2-3 sentence summary of the following legal document:\n\n"
            f"---\n{text}\n---"
        )

    def detailed_summary_system(self) -> str:
        return (
            "You are an expert Indian legal analyst specializing in analyzing court judgments "
            "and legal documents. Generate a comprehensive summary that covers:\n"
            "1. Background and context of the case\n"
            "2. Key facts and parties involved\n"
            "3. Legal issues raised\n"
            "4. Arguments presented\n"
            "5. Court's reasoning and decision\n"
            "6. Orders/directions given\n"
            "Use professional legal language but make it accessible. "
            "Include specific section numbers and act names when mentioned."
        )

    def detailed_summary_user(self, text: str) -> str:
        return (
            f"Provide a detailed summary of the following legal document:\n\n"
            f"---\n{text}\n---"
        )

    def key_findings_system(self) -> str:
        return (
            "You are an expert Indian legal analyst. Extract the key findings from the legal document. "
            "List each finding as a separate point. Focus on:\n"
            "- Legal conclusions reached\n"
            "- Facts established\n"
            "- Section violations identified\n"
            "- Evidence findings\n"
            "Return as a numbered list."
        )

    def key_findings_user(self, text: str) -> str:
        return (
            f"Extract the key findings from the following legal document:\n\n"
            f"---\n{text}\n---"
        )

    def verdict_system(self) -> str:
        return (
            "You are an expert Indian legal analyst. Identify the final verdict or outcome "
            "of the legal document. State clearly whether the accused was convicted/acquitted, "
            "whether the appeal was allowed/dismissed, or what the court ultimately decided. "
            "Include any sentence or punishment ordered."
        )

    def verdict_user(self, text: str) -> str:
        return (
            f"What is the final verdict in the following legal document?\n\n"
            f"---\n{text}\n---"
        )

    def principles_system(self) -> str:
        return (
            "You are an expert Indian legal analyst. Extract the legal principles established "
            "or applied in this document. These may include:\n"
            "- Ratio decidendi (reason for the decision)\n"
            "- Interpretation of statutes\n"
            "- Legal tests formulated\n"
            "- Principles of law applied\n"
            "Return as a numbered list."
        )

    def principles_user(self, text: str) -> str:
        return (
            f"What legal principles were established or applied in the following document?\n\n"
            f"---\n{text}\n---"
        )
