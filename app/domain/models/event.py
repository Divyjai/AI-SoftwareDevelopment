from dataclasses import dataclass

@dataclass
class BaseEvent:
    event_id: str
    timestamp: float
