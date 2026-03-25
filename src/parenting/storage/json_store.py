"""JSON file storage backend — atomic writes, pretty-printed, versioned."""

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


class JsonStore:
    """JSON file-based storage implementing the Store protocol.

    Each domain is stored as a separate JSON file inside `data_dir`.
    Writes are atomic: data is written to a temp file first, then moved
    into place via os.replace().
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        if data_dir is None:
            data_dir = Path("family_data")
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, domain: str) -> Path:
        return self._data_dir / f"{domain}.json"

    def load(self, domain: str) -> dict:
        """Load a domain's JSON data.

        Returns:
            The stored data dict, or empty dict if the domain has no data.
        """
        path = self._path_for(domain)
        if not path.exists():
            return {}
        text = path.read_text(encoding="utf-8")
        envelope = json.loads(text)
        return envelope.get("data", {})

    def save(self, domain: str, data: dict) -> None:
        """Save a domain's JSON data atomically.

        Writes to a temp file first, then replaces the target file.
        On Windows, retries on PermissionError (up to 3 times with 100ms sleep).
        """
        path = self._path_for(domain)
        envelope = {
            "version": 1,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        content = json.dumps(envelope, indent=2, ensure_ascii=False) + "\n"

        # Write to temp file in the same directory for atomic rename
        fd, tmp_path = tempfile.mkstemp(
            dir=self._data_dir, suffix=".tmp", prefix=f".{domain}_"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)

            # Atomic replace — retry on Windows PermissionError
            self._atomic_replace(tmp_path, str(path))
        except BaseException:
            # Clean up temp file on any failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def _atomic_replace(self, src: str, dst: str) -> None:
        """Replace dst with src atomically. Retries on Windows PermissionError."""
        max_retries = 3 if sys.platform == "win32" else 1
        for attempt in range(max_retries):
            try:
                os.replace(src, dst)
                return
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                else:
                    raise

    def exists(self, domain: str) -> bool:
        """Check if a domain has saved data."""
        return self._path_for(domain).exists()

    def delete(self, domain: str) -> None:
        """Delete a domain's data file."""
        path = self._path_for(domain)
        if path.exists():
            path.unlink()
