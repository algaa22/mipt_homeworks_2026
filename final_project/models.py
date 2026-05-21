from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    role: str
    content: str
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()