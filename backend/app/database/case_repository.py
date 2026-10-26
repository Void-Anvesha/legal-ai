"""Case repository boundary for generated police case packets."""
from typing import Dict, List

from ..models.intake import CaseFile


class CaseRepository:
    """In-memory implementation, replaceable with SQL storage."""

    def __init__(self):
        self.cases: Dict[str, CaseFile] = {}
        self.session_to_case: Dict[str, str] = {}

    def save_case(self, case_file: CaseFile) -> CaseFile:
        self.cases[case_file.case_id] = case_file
        self.session_to_case[case_file.session_id] = case_file.case_id
        return case_file

    def get_case(self, case_id: str) -> CaseFile:
        if case_id not in self.cases:
            raise KeyError("Case not found")
        return self.cases[case_id]

    def get_case_for_session(self, session_id: str) -> CaseFile:
        case_id = self.session_to_case.get(session_id)
        if not case_id:
            raise KeyError("Case file not found")
        return self.get_case(case_id)

    def list_cases(self) -> List[CaseFile]:
        return sorted(self.cases.values(), key=lambda case: case.created_at, reverse=True)
