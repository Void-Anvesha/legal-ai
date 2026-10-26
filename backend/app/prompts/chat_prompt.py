"""Prompt templates for legal chat assistant."""


class ChatPromptBuilder:
    """Builds prompts for the legal chat assistant."""

    def rag_system_prompt(self) -> str:
        return (
            "You are LegalAI, an expert Indian legal assistant. You help users understand "
            "legal documents, identify applicable laws, and answer questions about Indian law.\n\n"
            "Your capabilities:\n"
            "- Analyze legal documents (judgments, FIRs, charge sheets, petitions, contracts)\n"
            "- Identify applicable sections from BNS, IPC, IT Act, BNSS, BSA\n"
            "- Explain legal concepts in simple English\n"
            "- Summarize judgments and legal proceedings\n"
            "- Find similar cases and precedents\n"
            "- Explain possible punishments and legal implications\n\n"
            "Guidelines:\n"
            "1. Always base your answers on the provided context and Indian law\n"
            "2. Cite specific sections and act names when applicable\n"
            "3. If uncertain, clearly state that the information should be verified\n"
            "4. Use clear, professional language accessible to non-lawyers\n"
            "5. Note that BNS/BNSS/BSA replaced IPC/CrPC/IEA from July 1, 2024\n"
            "6. For legacy cases, explain both old and new section equivalents\n"
            "7. Always remind users that this is AI-assisted analysis and not legal advice\n"
            "8. When discussing punishments, mention both minimum and maximum penalties"
        )

    def rag_user_prompt(self, question: str, context: str) -> str:
        return (
            f"Based on the following legal context, answer the user's question.\n\n"
            f"LEGAL CONTEXT:\n---\n{context}\n---\n\n"
            f"USER QUESTION: {question}\n\n"
            f"Provide a comprehensive answer based on the context and your knowledge of Indian law. "
            f"If the context doesn't contain enough information, state that clearly and provide "
            f"general legal information where appropriate."
        )

    def explain_judgment_prompt(self, text: str) -> str:
        return (
            f"Explain the following judgment in simple terms that a non-lawyer can understand.\n"
            f"Cover: what happened, what the court decided, and what it means.\n\n"
            f"JUDGMENT:\n---\n{text}\n---"
        )

    def laws_apply_prompt(self, text: str) -> str:
        return (
            f"Based on the following legal document, which laws and sections apply?\n"
            f"Explain each applicable section and why it applies.\n\n"
            f"DOCUMENT:\n---\n{text}\n---"
        )

    def punishment_prompt(self, text: str) -> str:
        return (
            f"Based on the following legal document, what are the possible punishments?\n"
            f"Cover all applicable sections and their respective punishments.\n\n"
            f"DOCUMENT:\n---\n{text}\n---"
        )

    def similar_cases_prompt(self, text: str) -> str:
        return (
            f"Based on the following legal document, find and describe similar cases.\n"
            f"Focus on cases with similar facts, charges, and legal issues.\n\n"
            f"DOCUMENT:\n---\n{text}\n---"
        )
