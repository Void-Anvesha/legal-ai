"""Draft police-style complaint statements from structured facts."""
from ..models.intake import CaseFile, IncidentFacts, VictimProfile


class StatementDraftingAgent:
    """Create concise summaries and formal complaint drafts."""

    def create_summary(self, facts: IncidentFacts) -> str:
        incident_type = (facts.type or "complaint").replace("_", " ")
        location = facts.location or "an unspecified location"
        when = " ".join(part for part in [facts.date, facts.time] if part) or "an unspecified time"
        return f"The complaint concerns {incident_type} reported at {location} around {when}."

    def create_statement(self, victim: VictimProfile, facts: IncidentFacts) -> str:
        victim_line = victim.name or "The complainant"
        description = facts.description.strip() or "No detailed statement has been recorded yet."
        lines = [
            f"{victim_line} states as follows:",
            description,
            "",
            f"Incident category: {(facts.type or 'other complaint').replace('_', ' ')}.",
            f"Date/time: {' '.join(part for part in [facts.date, facts.time] if part) or 'Not fully specified'}.",
            f"Location: {facts.location or 'Not fully specified'}.",
        ]

        if facts.accused:
            lines.append(f"Accused/suspect details: {', '.join(facts.accused)}.")
        if facts.injuries:
            lines.append(f"Injury details mentioned: {', '.join(facts.injuries)}.")
        if facts.property_loss:
            lines.append(f"Property or loss mentioned: {', '.join(facts.property_loss)}.")
        if facts.evidence:
            lines.append(f"Available evidence mentioned: {', '.join(facts.evidence)}.")
        if facts.witnesses:
            lines.append(f"Witness details mentioned: {', '.join(facts.witnesses)}.")
        if facts.missing_information:
            lines.append(f"Details still requiring confirmation: {', '.join(facts.missing_information)}.")

        lines.append("This is an AI-prepared draft and must be verified by an authorized police officer.")
        return "\n".join(lines)

    def update_case_draft(self, case_file: CaseFile) -> CaseFile:
        updated = case_file.model_copy(deep=True)
        updated.summary = self.create_summary(updated.facts)
        updated.statement_draft = self.create_statement(updated.victim, updated.facts)
        return updated


statement_drafting_agent = StatementDraftingAgent()
