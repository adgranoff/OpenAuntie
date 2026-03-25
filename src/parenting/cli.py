"""OpenAuntie CLI — command-line interface for family management and consulting."""

import argparse
import json
import os
import sys
from pathlib import Path

from parenting.services.consultant_service import ConsultantService
from parenting.services.family_service import FamilyService
from parenting.storage.json_store import JsonStore


def _get_data_dir() -> Path:
    """Resolve the data directory from env var or default."""
    env_dir = os.environ.get("OPENAUNTIE_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path(__file__).parent.parent.parent / "family_data"


def _make_store() -> JsonStore:
    """Create a JsonStore pointed at the configured data directory."""
    return JsonStore(data_dir=_get_data_dir())


def _cmd_setup(args: argparse.Namespace) -> None:
    """Handle the 'setup' command."""
    from parenting.models.family import FamilyProfile, Parent

    store = _make_store()
    svc = FamilyService(store)

    profile = FamilyProfile(
        family_name=args.family_name,
        parents=[
            Parent(id="parent-1", name=args.parent_name, role="parent")
        ],
    )
    svc.save_family(profile)
    print(
        f"Family profile created for the {args.family_name} family. "
        f"Add children with: parenting add-child --id <id> --name <name> "
        f"--dob YYYY-MM-DD"
    )


def _cmd_consult(args: argparse.Namespace) -> None:
    """Handle the 'consult' command."""
    store = _make_store()
    svc = ConsultantService(store=store)
    question = " ".join(args.question)
    result = svc.consult(question)
    print(json.dumps(result, indent=2, default=str))


def _cmd_summary(args: argparse.Namespace) -> None:
    """Handle the 'summary' command."""
    store = _make_store()
    svc = ConsultantService(store=store)
    result = svc.weekly_summary(period_days=args.days)
    print(json.dumps(result, indent=2, default=str))


def _cmd_export(args: argparse.Namespace) -> None:
    """Handle the 'export' command."""
    store = _make_store()
    svc = FamilyService(store)
    profile = svc.get_family()
    if profile is None:
        print("No family profile found. Run 'parenting setup' first.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(profile.model_dump(mode="json"), indent=2, default=str))


def main() -> None:
    """Entry point for the OpenAuntie CLI."""
    parser = argparse.ArgumentParser(
        description="OpenAuntie — Evidence-based parenting agent"
    )
    subparsers = parser.add_subparsers(dest="command")

    # setup command
    setup_parser = subparsers.add_parser(
        "setup", help="Set up your family profile"
    )
    setup_parser.add_argument("--family-name", required=True)
    setup_parser.add_argument("--parent-name", required=True)

    # consult command
    consult_parser = subparsers.add_parser(
        "consult", help="Ask Auntie a parenting question"
    )
    consult_parser.add_argument("question", nargs="+")

    # summary command
    summary_parser = subparsers.add_parser(
        "summary", help="Weekly summary"
    )
    summary_parser.add_argument("--days", type=int, default=7)

    # export command
    subparsers.add_parser("export", help="Export all data as JSON")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "setup": _cmd_setup,
        "consult": _cmd_consult,
        "summary": _cmd_summary,
        "export": _cmd_export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
