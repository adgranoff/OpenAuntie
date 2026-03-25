"""Tests for the JSON storage backend."""

import json
from pathlib import Path

from parenting.storage.json_store import JsonStore


class TestJsonStoreLoadSaveRoundtrip:
    def test_save_and_load_roundtrip(self, tmp_store: JsonStore) -> None:
        # given
        data = {"name": "TestFamily", "children": ["max", "emma"]}

        # when
        tmp_store.save("family", data)
        loaded = tmp_store.load("family")

        # then
        assert loaded == data

    def test_load_returns_empty_dict_for_nonexistent_domain(
        self, tmp_store: JsonStore
    ) -> None:
        # given — no data saved

        # when
        result = tmp_store.load("nonexistent")

        # then
        assert result == {}

    def test_roundtrip_preserves_nested_structures(
        self, tmp_store: JsonStore
    ) -> None:
        # given
        data = {
            "profile": {
                "family_name": "Smith",
                "children": [
                    {"id": "kid1", "name": "Kid One"},
                    {"id": "kid2", "name": "Kid Two"},
                ],
            },
            "count": 42,
            "flag": True,
        }

        # when
        tmp_store.save("complex", data)
        loaded = tmp_store.load("complex")

        # then
        assert loaded == data


class TestJsonStoreExists:
    def test_exists_returns_false_for_missing_domain(
        self, tmp_store: JsonStore
    ) -> None:
        # given — no data saved

        # when / then
        assert tmp_store.exists("missing") is False

    def test_exists_returns_true_after_save(self, tmp_store: JsonStore) -> None:
        # given
        tmp_store.save("present", {"key": "value"})

        # when / then
        assert tmp_store.exists("present") is True


class TestJsonStoreDelete:
    def test_delete_removes_existing_file(self, tmp_store: JsonStore) -> None:
        # given
        tmp_store.save("to_delete", {"key": "value"})
        assert tmp_store.exists("to_delete") is True

        # when
        tmp_store.delete("to_delete")

        # then
        assert tmp_store.exists("to_delete") is False
        assert tmp_store.load("to_delete") == {}

    def test_delete_nonexistent_domain_is_noop(
        self, tmp_store: JsonStore
    ) -> None:
        # given — no data saved

        # when — should not raise
        tmp_store.delete("nonexistent")

        # then
        assert tmp_store.exists("nonexistent") is False


class TestJsonStoreAtomicWrite:
    def test_saved_file_has_valid_json_envelope(
        self, tmp_store: JsonStore
    ) -> None:
        # given
        data = {"key": "value"}

        # when
        tmp_store.save("envelope_test", data)

        # then — read raw file and verify envelope structure
        path = tmp_store._path_for("envelope_test")
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw["version"] == 1
        assert "last_updated" in raw
        assert raw["data"] == data

    def test_saved_file_is_pretty_printed(self, tmp_store: JsonStore) -> None:
        # given
        data = {"key": "value"}

        # when
        tmp_store.save("pretty_test", data)

        # then — file should contain indented JSON (not single-line)
        path = tmp_store._path_for("pretty_test")
        text = path.read_text(encoding="utf-8")
        assert "\n" in text
        # indent=2 means nested keys are indented with spaces
        assert '  "data"' in text

    def test_file_is_not_corrupted_after_save(
        self, tmp_store: JsonStore
    ) -> None:
        # given — save multiple times to the same domain
        for i in range(5):
            tmp_store.save("stress", {"iteration": i})

        # when
        loaded = tmp_store.load("stress")

        # then — last write wins, file is valid
        assert loaded == {"iteration": 4}


class TestJsonStoreDirectoryCreation:
    def test_creates_data_dir_if_missing(self, tmp_path: Path) -> None:
        # given
        new_dir = tmp_path / "sub" / "deep"
        assert not new_dir.exists()

        # when
        store = JsonStore(data_dir=new_dir)

        # then
        assert new_dir.exists()
        store.save("test", {"ok": True})
        assert store.load("test") == {"ok": True}
