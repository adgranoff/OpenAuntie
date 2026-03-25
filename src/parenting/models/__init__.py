"""Pydantic v2 models — source of truth for all OpenAuntie data."""

from parenting.models.behavior import (
    ChoreCompletion,
    ChoreDefinition,
    ConsequenceLog,
    PointsConfig,
    PointsEntry,
    RewardOption,
)
from parenting.models.education import HomeworkEntry, LearningGoal, ReadingEntry
from parenting.models.emotional import ConflictRecord, DevelopmentalMilestone, MoodEntry
from parenting.models.family import Child, FamilyProfile, Parent
from parenting.models.feedback import AdviceFeedback
from parenting.models.health import Appointment, GrowthRecord, Medication, MedicationLog
from parenting.models.journal import JournalEntry
from parenting.models.research import ResearchUpdate
from parenting.models.routines import RoutineDefinition, RoutineExecution, RoutineStep

__all__ = [
    "AdviceFeedback",
    "Appointment",
    "Child",
    "ChoreCompletion",
    "ChoreDefinition",
    "ConflictRecord",
    "ConsequenceLog",
    "DevelopmentalMilestone",
    "FamilyProfile",
    "GrowthRecord",
    "HomeworkEntry",
    "JournalEntry",
    "LearningGoal",
    "Medication",
    "MedicationLog",
    "MoodEntry",
    "Parent",
    "PointsConfig",
    "PointsEntry",
    "ReadingEntry",
    "ResearchUpdate",
    "RewardOption",
    "RoutineDefinition",
    "RoutineExecution",
    "RoutineStep",
]
