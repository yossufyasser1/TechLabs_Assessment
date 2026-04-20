"""Note data model used by the storage layer."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Note:
    """A single note in the system."""

    id: str
    title: str
    body: str
    tags: list[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """Serialise for tool responses — the LLM sees this format."""
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }