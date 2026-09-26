"""Data models used by the save-set library."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SaveSet:
    """Represent one named save snapshot and its library metadata."""

    id: str
    name: str
    description: str = ""
    thumbnail: str = ""

    created: Optional[str] = None
    modified: Optional[str] = None

    active: bool = False


    @property
    def created_datetime(self):
        """Return the creation timestamp as a datetime when it is valid."""

        if not self.created:
            return None

        try:
            return datetime.fromisoformat(self.created)
        except ValueError:
            return None

    def to_dict(self):
        """Serialize the model to the metadata JSON representation."""

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "created": self.created,
            "modified": self.modified,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data):
        """Build a save set from metadata, using defaults for missing fields."""

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            thumbnail=data.get("thumbnail", ""),
            created=data.get("created"),
            modified=data.get("modified"),
            active=data.get("active", False)
        )