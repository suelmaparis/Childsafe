from abc import ABC, abstractmethod

from app.monitoring.candidate import (
    MonitoringCandidate,
)


class BaseCollector(ABC):
    """
    Base interface for all ChildSafe monitoring collectors.
    """

    platform: str
    channel: str

    @abstractmethod
    def collect(
        self,
    ) -> list[MonitoringCandidate]:
        """
        Collect public content candidates.

        Every collector must return MonitoringCandidate objects.
        """

        raise NotImplementedError