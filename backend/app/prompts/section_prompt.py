"""Prompt templates for legal section prediction."""


class SectionPromptBuilder:
    """Builds prompts for legal section analysis and prediction."""

    def section_prediction_system(self) -> str:
        return (
            "You are an expert Indian legal analyst with deep knowledge of:\n"
            "- Bharatiya Nyaya Sanhita (BNS) 2023\n"
            "- Indian Penal Code (IPC) 1860\n"
            "- Information Technology Act 2000\n"
            "- Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023\n"
            "- Bharatiya Sakshya Adhiniyam (BSA) 2023\n"
            "- Code of Criminal Procedure (CrPC) 1973\n"
            "- Indian Evidence Act 1872\n\n"
            "Given a legal document, identify ALL applicable sections from these acts. "
            "For each section, explain:\n"
            "1. The section number and act name\n"
            "2. Why it applies to this case\n"
            "3. The punishment prescribed\n"
            "4. Whether it is cognizable/bailable\n\n"
            "Format your response as a structured list."
        )

    def section_prediction_user(self, text: str) -> str:
        return (
            f"Identify all applicable legal sections in the following document:\n\n"
            f"---\n{text}\n---\n\n"
            f"For each section, provide:\n"
            f"- Act name and section number\n"
            f"- Why it applies\n"
            f"- Punishment details\n"
            f"- Cognizable/Bailable status"
        )

    def section_explanation_system(self) -> str:
        return (
            "You are an expert Indian legal educator. Explain legal sections in simple, "
            "clear English that a non-lawyer can understand. For each section:\n"
            "1. State the section in plain language\n"
            "2. Explain what behaviour it covers\n"
            "3. Describe the punishment\n"
            "4. Give a real-world example\n"
            "5. Note any important judicial interpretations"
        )

    def section_explanation_user(self, act: str, section_number: str) -> str:
        return (
            f"Explain the following legal section in simple English:\n"
            f"Act: {act}\n"
            f"Section: {section_number}\n\n"
            f"Provide a clear explanation covering:\n"
            f"- What this section means in simple terms\n"
            f"- What behaviour it prohibits\n"
            f"- The punishment it carries\n"
            f"- A real-world example\n"
            f"- Important court judgments interpreting this section"
        )
