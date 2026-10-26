"""Conversation memory utilities for intake sessions."""
from typing import List

from ..models.intake import ConversationMessage


class ConversationMemory:
    """Build transcript views from stored conversation messages."""

    def transcript(self, messages: List[ConversationMessage]) -> str:
        return "\n".join(f"{message.role.value}: {message.content}" for message in messages)

    def victim_text(self, messages: List[ConversationMessage]) -> str:
        return "\n".join(
            message.content
            for message in messages
            if message.role.value == "victim"
        )


conversation_memory = ConversationMemory()
