"""Audit logging helpers for intake and officer review events."""
from datetime import datetime
from typing import Any, Dict, Optional


class AuditLogger:
    """Create consistent audit entries for case files and sessions."""

    def event(self, event: str, message: str, **metadata: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "event": event,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if metadata:
            payload["metadata"] = metadata
        return payload

    def session_event(self, session_id: str, event: str, message: str) -> Dict[str, Any]:
        return self.event(event, message, session_id=session_id)

    def officer_event(
        self,
        case_id: str,
        officer_id: Optional[str],
        event: str,
        message: str,
        **metadata: Any,
    ) -> Dict[str, Any]:
        return self.event(
            event,
            message,
            case_id=case_id,
            officer_id=officer_id,
            **metadata,
        )


audit_logger = AuditLogger()
