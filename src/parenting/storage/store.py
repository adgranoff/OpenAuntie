"""Storage protocol — defines the interface all storage backends must implement."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Store(Protocol):
    """Protocol for domain-based JSON storage.

    Each domain maps to one logical data file. Implementations handle
    serialization, persistence, and atomicity.
    """

    def load(self, domain: str) -> dict:
        """Load a domain's JSON data.

        Args:
            domain: The storage domain key (e.g. "family_profile").

        Returns:
            The stored data dict, or empty dict if the domain has no data.
        """
        ...

    def save(self, domain: str, data: dict) -> None:
        """Save a domain's JSON data atomically.

        Args:
            domain: The storage domain key.
            data: The data dict to persist.
        """
        ...

    def exists(self, domain: str) -> bool:
        """Check if a domain has saved data.

        Args:
            domain: The storage domain key.

        Returns:
            True if data exists for the domain.
        """
        ...

    def delete(self, domain: str) -> None:
        """Delete a domain's data file.

        Args:
            domain: The storage domain key.
        """
        ...
