"""Family service — CRUD operations for the family profile and children."""

from datetime import date

from parenting.models.family import Child, FamilyProfile
from parenting.storage.store import Store

FAMILY_DOMAIN = "family_profile"


class FamilyService:
    """Business logic for managing the family profile.

    Takes a Store backend and operates on the 'family_profile' domain.
    """

    def __init__(self, store: Store) -> None:
        self._store = store

    def get_family(self) -> FamilyProfile | None:
        """Load the family profile from storage.

        Returns:
            The FamilyProfile, or None if no profile exists.
        """
        if not self._store.exists(FAMILY_DOMAIN):
            return None
        data = self._store.load(FAMILY_DOMAIN)
        if not data:
            return None
        return FamilyProfile.model_validate(data)

    def save_family(self, profile: FamilyProfile) -> None:
        """Save the family profile to storage."""
        self._store.save(FAMILY_DOMAIN, profile.model_dump(mode="json"))

    def get_child(self, child_id: str) -> Child | None:
        """Find a child by ID.

        Args:
            child_id: The child's unique identifier.

        Returns:
            The Child, or None if not found or no family profile exists.
        """
        profile = self.get_family()
        if profile is None:
            return None
        for child in profile.children:
            if child.id == child_id:
                return child
        return None

    def add_child(self, child: Child) -> FamilyProfile:
        """Add a child to the family profile.

        Args:
            child: The Child to add.

        Returns:
            The updated FamilyProfile.

        Raises:
            ValueError: If a child with the same ID already exists.
            RuntimeError: If no family profile exists yet.
        """
        profile = self.get_family()
        if profile is None:
            raise RuntimeError(
                "No family profile exists. Create one before adding children."
            )
        for existing in profile.children:
            if existing.id == child.id:
                raise ValueError(
                    f"Child with id '{child.id}' already exists in the family profile."
                )
        profile.children.append(child)
        self.save_family(profile)
        return profile

    def update_child(self, child_id: str, **kwargs: object) -> Child:
        """Update fields on an existing child.

        Args:
            child_id: The child's unique identifier.
            **kwargs: Field names and new values to apply.

        Returns:
            The updated Child.

        Raises:
            KeyError: If the child is not found.
        """
        profile = self.get_family()
        if profile is None:
            raise KeyError(f"Child '{child_id}' not found (no family profile).")
        for i, child in enumerate(profile.children):
            if child.id == child_id:
                updated_data = child.model_dump()
                updated_data.update(kwargs)
                updated_child = Child.model_validate(updated_data)
                profile.children[i] = updated_child
                self.save_family(profile)
                return updated_child
        raise KeyError(f"Child '{child_id}' not found.")

    def get_child_age_years(self, child_id: str) -> float:
        """Compute a child's age in decimal years.

        Args:
            child_id: The child's unique identifier.

        Returns:
            Age in years as a float (e.g. 3.5).

        Raises:
            KeyError: If the child is not found.
        """
        child = self.get_child(child_id)
        if child is None:
            raise KeyError(f"Child '{child_id}' not found.")
        today = date.today()
        delta = today - child.date_of_birth
        return delta.days / 365.25
