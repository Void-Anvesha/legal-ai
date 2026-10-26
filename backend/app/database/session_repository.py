"""Session repository boundary for intake storage."""
from typing import Dict, List

from ..models.intake import ConversationMessage, IntakeSession


class SessionRepository:
    """In-memory implementation, replaceable with SQL storage."""

    def __init__(self):
        self.sessions: Dict[str, IntakeSession] = {}
        self.messages: Dict[str, List[ConversationMessage]] = {}

    def save_session(self, session: IntakeSession) -> IntakeSession:
        self.sessions[session.session_id] = session
        self.messages.setdefault(session.session_id, [])
        return session

    def get_session(self, session_id: str) -> IntakeSession:
        if session_id not in self.sessions:
            raise KeyError("Intake session not found")
        return self.sessions[session_id]

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        self.messages.setdefault(message.session_id, []).append(message)
        return message

    def list_messages(self, session_id: str) -> List[ConversationMessage]:
        return self.messages.get(session_id, [])
