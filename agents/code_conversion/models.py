from dataclasses import dataclass
from typing import List

@dataclass
class DataState:
    """Data class to hold DataFrame state information"""
    head: str
    info: str
    null_info: str

@dataclass
class CleaningHistoryEntry:
    """Data class for cleaning history entries"""
    iteration: int
    instruction: str
    code: str
    successful: bool

class CleaningHistory:
    """Manages cleaning history entries"""
    def __init__(self):
        self.entries: List[CleaningHistoryEntry] = []

    def add_entry(self, entry: CleaningHistoryEntry):
        self.entries.append(entry)

    def get_all_entries(self) -> List[CleaningHistoryEntry]:
        return self.entries