from abc import ABC, abstractmethod
from app.domain.models.event import BaseEvent

class EventBus(ABC):
    @abstractmethod
    def publish(self, event: BaseEvent):
        pass
