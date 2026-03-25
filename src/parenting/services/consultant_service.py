"""Consultant service — context assembly engine for parenting questions.

The consultant does NOT call an LLM. It assembles rich family context,
developmental expectations, and evidence-based research so the calling
LLM can give great, personalized advice.
"""

import re
from pathlib import Path

from parenting.services.family_service import FamilyService
from parenting.storage.store import Store

# Default knowledge directory: project_root/knowledge/
_DEFAULT_KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"

# Mapping from question keywords to knowledge files and domains.
# Each entry: keyword -> list of (knowledge_filename, domain_tag)
_TOPIC_MAP: dict[str, list[tuple[str, str]]] = {
    # Homework and learning
    "homework": [("homework_and_learning.md", "learning")],
    "learning": [("homework_and_learning.md", "learning")],
    "school": [("homework_and_learning.md", "learning")],
    "grades": [("homework_and_learning.md", "learning")],
    "studying": [("homework_and_learning.md", "learning")],
    "reading": [("homework_and_learning.md", "learning")],
    # Routines and sleep
    "bedtime": [("routines_research.md", "routines")],
    "sleep": [("routines_research.md", "routines")],
    "routine": [("routines_research.md", "routines")],
    "routines": [("routines_research.md", "routines")],
    "morning": [("routines_research.md", "routines")],
    "nap": [("routines_research.md", "routines")],
    # Sibling dynamics
    "sibling": [("sibling_dynamics.md", "siblings")],
    "siblings": [("sibling_dynamics.md", "siblings")],
    "fighting": [
        ("sibling_dynamics.md", "siblings"),
        ("emotion_coaching.md", "emotional"),
    ],
    "sharing": [("sibling_dynamics.md", "siblings")],
    "jealous": [("sibling_dynamics.md", "siblings")],
    "jealousy": [("sibling_dynamics.md", "siblings")],
    # Emotion coaching
    "emotion": [("emotion_coaching.md", "emotional")],
    "emotions": [("emotion_coaching.md", "emotional")],
    "feelings": [("emotion_coaching.md", "emotional")],
    "angry": [("emotion_coaching.md", "emotional")],
    "anger": [("emotion_coaching.md", "emotional")],
    "tantrum": [("emotion_coaching.md", "emotional")],
    "tantrums": [("emotion_coaching.md", "emotional")],
    "meltdown": [("emotion_coaching.md", "emotional")],
    "crying": [("emotion_coaching.md", "emotional")],
    "anxiety": [("emotion_coaching.md", "emotional")],
    "anxious": [("emotion_coaching.md", "emotional")],
    "fear": [("emotion_coaching.md", "emotional")],
    "scared": [("emotion_coaching.md", "emotional")],
    # Behavior systems
    "behavior": [("behavior_systems.md", "behavior")],
    "behaviour": [("behavior_systems.md", "behavior")],
    "chore": [("behavior_systems.md", "behavior")],
    "chores": [("behavior_systems.md", "behavior")],
    "reward": [("behavior_systems.md", "behavior")],
    "rewards": [("behavior_systems.md", "behavior")],
    "points": [("behavior_systems.md", "behavior")],
    "consequence": [("behavior_systems.md", "behavior")],
    "consequences": [("behavior_systems.md", "behavior")],
    "discipline": [("positive_discipline.md", "discipline")],
    "punishment": [("positive_discipline.md", "discipline")],
    "timeout": [("positive_discipline.md", "discipline")],
    "time-out": [("positive_discipline.md", "discipline")],
    # Positive discipline
    "limit": [("positive_discipline.md", "discipline")],
    "limits": [("positive_discipline.md", "discipline")],
    "boundary": [("positive_discipline.md", "discipline")],
    "boundaries": [("positive_discipline.md", "discipline")],
    # Screen time
    "screen": [("screen_time.md", "screen_time")],
    "screens": [("screen_time.md", "screen_time")],
    "tablet": [("screen_time.md", "screen_time")],
    "phone": [("screen_time.md", "screen_time")],
    "gaming": [("screen_time.md", "screen_time")],
    "videogame": [("screen_time.md", "screen_time")],
    "tv": [("screen_time.md", "screen_time")],
    "television": [("screen_time.md", "screen_time")],
    # Family communication
    "communication": [("family_communication.md", "communication")],
    "talking": [("family_communication.md", "communication")],
    "listening": [("family_communication.md", "communication")],
    "yelling": [("family_communication.md", "communication")],
    "arguing": [("family_communication.md", "communication")],
    # Collaborative problem solving
    "problem": [("collaborative_problem_solving.md", "problem_solving")],
    "negotiate": [("collaborative_problem_solving.md", "problem_solving")],
    "negotiation": [("collaborative_problem_solving.md", "problem_solving")],
    "collaborate": [("collaborative_problem_solving.md", "problem_solving")],
    "compromise": [("collaborative_problem_solving.md", "problem_solving")],
    # Developmental stages (always loaded via get_age_expectations)
    "development": [("developmental_stages.md", "development")],
    "milestone": [("developmental_stages.md", "development")],
    "milestones": [("developmental_stages.md", "development")],
    "age-appropriate": [("developmental_stages.md", "development")],
}

# Keywords that trigger safety referrals.
_HARD_REFERRAL_KEYWORDS = [
    "self-harm",
    "self harm",
    "selfharm",
    "suicide",
    "suicidal",
    "kill myself",
    "kill themselves",
    "abuse",
    "abused",
    "abusing",
    "molest",
    "molestation",
    "sexual abuse",
    "hitting the child",
    "hurting the child",
]

_SOFT_REFERRAL_KEYWORDS = [
    "regression",
    "regressing",
    "medication",
    "medicate",
    "adhd medication",
    "diagnosis",
    "diagnose",
    "diagnosed",
    "disorder",
    "autism",
    "spectrum",
    "asd",
    "depression",
    "depressed",
    "eating disorder",
    "anorexia",
    "bulimia",
    "therapy",
    "therapist",
    "psychologist",
    "psychiatrist",
]

# Age bands as (min_age, max_age, header_text) for matching developmental stages.
_AGE_BANDS: list[tuple[float, float, str]] = [
    (0, 2, "## Ages 0-2 (Infant / Toddler)"),
    (3, 5, "## Ages 3-5 (Preschool)"),
    (5, 7, "## Ages 5-7 (Early Elementary)"),
    (8, 10, "## Ages 8-10 (Middle Elementary)"),
    (10, 12, "## Ages 10-12 (Upper Elementary / Pre-Adolescence)"),
    (13, 15, "## Ages 13-15 (Early Adolescence)"),
    (16, 18, "## Ages 16-18 (Late Adolescence)"),
]


class ConsultantService:
    """Context assembly engine for parenting questions.

    Assembles family context, developmental expectations, and evidence-based
    research from the knowledge base. Does NOT call an LLM.
    """

    def __init__(
        self, store: Store, knowledge_dir: Path | None = None
    ) -> None:
        self.store = store
        self.knowledge_dir = knowledge_dir or _DEFAULT_KNOWLEDGE_DIR
        self.family_service = FamilyService(store)

    def consult(self, question: str) -> dict:
        """Assemble full family context for a parenting question.

        Args:
            question: The parenting question from the user.

        Returns:
            Structured dict with family_context, relevant_research,
            developmental_context, safety_check, and the original question.
        """
        # Detect topics from question keywords
        topics = self._detect_topics(question)
        knowledge_files = set()
        domains = set()
        for files_and_domains in topics.values():
            for filename, domain in files_and_domains:
                knowledge_files.add(filename)
                domains.add(domain)

        # Build family context
        family_context = self._build_family_context()

        # Load relevant research from knowledge base
        relevant_research: dict[str, str] = {}
        for filename in knowledge_files:
            content = self._load_knowledge(filename)
            if content is not None:
                relevant_research[filename] = content

        # Build developmental context for each child
        developmental_context = self._build_developmental_context()

        # Safety check
        safety = self.check_safety(question)

        return {
            "question": question,
            "family_context": family_context,
            "relevant_domains": sorted(domains),
            "developmental_context": developmental_context,
            "relevant_research": relevant_research,
            "safety_check": safety,
        }

    def weekly_summary(self, period_days: int = 7) -> dict:
        """Generate cross-domain summary for recent period.

        Args:
            period_days: Number of days to look back (default 7).

        Returns:
            Per-child summaries with behavior, routines, emotional,
            highlights, and concerns sections.
        """
        profile = self.family_service.get_family()
        if profile is None:
            return {"error": "No family profile found. Run setup first."}

        child_summaries: dict[str, dict] = {}
        for child in profile.children:
            child_summaries[child.id] = {
                "name": child.name,
                "age": child.age_description,
                "behavior": {
                    "points_earned": 0,
                    "points_spent": 0,
                    "chore_completion_rate": 0.0,
                    "positive_to_negative_ratio": 0.0,
                },
                "routines": {
                    "completion_rate": 0.0,
                    "current_streak": 0,
                    "regressions": [],
                },
                "emotional": {
                    "mood_trend": "no data",
                    "conflict_count": 0,
                },
                "highlights": [],
                "concerns": [],
            }

        return {
            "period_days": period_days,
            "family_name": profile.family_name,
            "children": child_summaries,
        }

    def get_age_expectations(self, child_id: str) -> dict:
        """Get developmental expectations for a child's current age.

        Args:
            child_id: The child's unique identifier.

        Returns:
            Dict with child info, age band label, and the relevant section
            from developmental_stages.md.

        Raises:
            KeyError: If the child is not found.
        """
        child = self.family_service.get_child(child_id)
        if child is None:
            raise KeyError(f"Child '{child_id}' not found.")

        age_years = self.family_service.get_child_age_years(child_id)
        band_label, section_content = self._find_age_band(age_years)

        return {
            "child_id": child.id,
            "child_name": child.name,
            "age": child.age_description,
            "age_years": round(age_years, 1),
            "age_band": band_label,
            "expectations": section_content,
        }

    def check_safety(self, text: str) -> dict:
        """Check text for topics requiring professional referral.

        Args:
            text: The text to scan (typically the user's question).

        Returns:
            Dict with needs_referral, referral_type, referral_reason,
            and referral_message.
        """
        text_lower = text.lower()

        # Check hard referrals first (more serious)
        for keyword in _HARD_REFERRAL_KEYWORDS:
            if keyword in text_lower:
                return {
                    "needs_referral": True,
                    "referral_type": "hard",
                    "referral_reason": f"Detected safety-critical topic: '{keyword}'",
                    "referral_message": (
                        "This topic is beyond what OpenAuntie can safely address. "
                        "Please reach out to a qualified professional immediately. "
                        "If someone is in immediate danger, call 911 or your local "
                        "emergency number. For crisis support, contact the 988 "
                        "Suicide & Crisis Lifeline (call or text 988)."
                    ),
                }

        # Check soft referrals (professional guidance recommended)
        for keyword in _SOFT_REFERRAL_KEYWORDS:
            if keyword in text_lower:
                return {
                    "needs_referral": True,
                    "referral_type": "soft",
                    "referral_reason": (
                        f"Detected topic that may benefit from professional "
                        f"guidance: '{keyword}'"
                    ),
                    "referral_message": (
                        "OpenAuntie can share general research and strategies, "
                        "but this topic may benefit from professional guidance. "
                        "Consider consulting your pediatrician or a child "
                        "psychologist for personalized assessment and support."
                    ),
                }

        return {
            "needs_referral": False,
            "referral_type": None,
            "referral_reason": None,
            "referral_message": None,
        }

    # ---- Private helpers ----

    def _detect_topics(
        self, question: str
    ) -> dict[str, list[tuple[str, str]]]:
        """Map question keywords to knowledge files and domains.

        Args:
            question: The user's question text.

        Returns:
            Dict mapping matched keywords to their (filename, domain) pairs.
        """
        question_lower = question.lower()
        # Tokenize into words for whole-word matching
        words = set(re.findall(r"[a-z]+(?:-[a-z]+)*", question_lower))
        matched: dict[str, list[tuple[str, str]]] = {}
        for keyword, files_and_domains in _TOPIC_MAP.items():
            # Match if keyword appears as a whole word or as a substring
            # for compound keywords like "age-appropriate"
            if keyword in words or keyword in question_lower:
                matched[keyword] = files_and_domains
        return matched

    def _load_knowledge(self, filename: str) -> str | None:
        """Read a knowledge markdown file and return its content.

        Args:
            filename: The knowledge file name (e.g. "homework_and_learning.md").

        Returns:
            The file content as a string, or None if the file doesn't exist.
        """
        path = self.knowledge_dir / filename
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def _build_family_context(self) -> dict | None:
        """Build family context dict from stored profile.

        Returns:
            Dict with family info and children details, or None if no profile.
        """
        profile = self.family_service.get_family()
        if profile is None:
            return None

        children_context = []
        for child in profile.children:
            children_context.append({
                "id": child.id,
                "name": child.name,
                "age": child.age_description,
                "temperament_notes": child.temperament_notes,
                "strengths": child.strengths,
                "challenges": child.challenges,
                "special_considerations": child.special_considerations,
            })

        return {
            "family_name": profile.family_name,
            "parents": [
                {"name": p.name, "role": p.role} for p in profile.parents
            ],
            "children": children_context,
            "values": profile.values,
            "timezone": profile.timezone,
        }

    def _build_developmental_context(self) -> list[dict]:
        """Build developmental context for all children.

        Returns:
            List of dicts with child info and age-band expectations.
        """
        profile = self.family_service.get_family()
        if profile is None:
            return []

        contexts = []
        for child in profile.children:
            try:
                age_years = self.family_service.get_child_age_years(child.id)
                band_label, section = self._find_age_band(age_years)
                contexts.append({
                    "child_id": child.id,
                    "child_name": child.name,
                    "age": child.age_description,
                    "age_band": band_label,
                    "expectations": section,
                })
            except KeyError:
                continue
        return contexts

    def _find_age_band(self, age_years: float) -> tuple[str, str]:
        """Find the developmental age band for a given age.

        Args:
            age_years: Age in decimal years.

        Returns:
            Tuple of (band_label, section_content) from developmental_stages.md.
        """
        content = self._load_knowledge("developmental_stages.md")
        if content is None:
            return ("unknown", "Developmental stages data not available.")

        # Find the matching age band
        target_header = None
        for min_age, max_age, header in _AGE_BANDS:
            if min_age <= age_years <= max_age:
                target_header = header
                break

        # If age doesn't fit any band, find closest
        if target_header is None:
            if age_years < 0:
                target_header = _AGE_BANDS[0][2]
            else:
                target_header = _AGE_BANDS[-1][2]

        # Extract the section from the content
        band_label = target_header.replace("## ", "")
        start_idx = content.find(target_header)
        if start_idx == -1:
            return (band_label, "Section not found in knowledge base.")

        # Find the next section of the same level (## header)
        next_section = content.find("\n## ", start_idx + len(target_header))
        if next_section == -1:
            section_content = content[start_idx:]
        else:
            section_content = content[start_idx:next_section]

        return (band_label, section_content.strip())
