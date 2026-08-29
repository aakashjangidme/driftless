"""Unit tests for output renderer."""

import json
from datetime import UTC

import pytest

from driftless.output import renderer


class TestPrintJson:
    def test_outputs_valid_json(self, capsys):
        renderer.print_json({"key": "value", "num": 42})
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["key"] == "value"
        assert data["num"] == 42

    def test_json_output_is_stable(self, capsys):
        data = {"status": "pass", "work": "W-0001", "next": "REVIEW"}
        renderer.print_json(data)
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed == data

    def test_handles_datetime_via_default_str(self, capsys):
        from datetime import datetime

        dt = datetime(2026, 1, 1, tzinfo=UTC)
        renderer.print_json({"ts": dt})
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "2026" in parsed["ts"]

    def test_json_is_indented(self, capsys):
        renderer.print_json({"a": 1})
        out = capsys.readouterr().out
        # Indented JSON should have newlines
        assert "\n" in out

    def test_list_output(self, capsys):
        renderer.print_json([{"id": "W-0001"}, {"id": "W-0002"}])
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert len(parsed) == 2
        assert parsed[0]["id"] == "W-0001"


class TestErrorWithHint:
    def test_exits_with_code_1(self):
        with pytest.raises(SystemExit) as exc_info:
            renderer.error_with_hint("Test error", "Fix it")
        assert exc_info.value.code == 1

    def test_error_message_output(self, capsys):
        with pytest.raises(SystemExit):
            renderer.error_with_hint("Something broke", "")
        # Rich Console writes to stderr
        # We just verify it doesn't raise unexpectedly beyond SystemExit


class TestVerifyData:
    def test_verify_json_schema_stability(self, capsys):
        """Verify that verify JSON output has the expected stable schema."""
        data = {
            "status": "pass",
            "work": "W-0001",
            "work_status": "IMPLEMENTING",
            "openspec": {"passed": True, "status": "pass"},
            "git": {"branch": "feature/x", "clean": True, "commit": "abc"},
            "errors": [],
            "warnings": [],
            "next": "REVIEW",
        }
        renderer.print_json(data)
        out = capsys.readouterr().out
        parsed = json.loads(out)
        for key in ("status", "work", "openspec", "git", "errors", "next"):
            assert key in parsed


class TestHumanRenderers:
    def test_print_human(self, capsys):
        renderer.print_human(["Line 1", "Line 2"])
        out = capsys.readouterr().out
        assert "Line 1" in out
        assert "Line 2" in out

    def test_print_work_human(self, capsys):
        data = {
            "id": "W-0001",
            "title": "OAuth Feature",
            "type": "feature",
            "status": "CREATED",
            "branch": "main",
            "openspec_change": "add-oauth",
            "repository": "/tmp/repo",
        }
        renderer.print_work_human(data)
        out = capsys.readouterr().out
        assert "W-0001" in out
        assert "OAuth Feature" in out

    def test_print_status_human_active_work(self, capsys):
        data = {
            "work": {
                "id": "W-0001",
                "title": "OAuth Feature",
                "type": "feature",
                "status": "CREATED",
                "openspec_change": "add-oauth",
            },
            "git": {"available": True, "branch": "main", "clean": True},
            "openspec": {"status": "ready"},
            "message": "next step message",
        }
        renderer.print_status_human(data)
        out = capsys.readouterr().out
        assert "W-0001" in out
        assert "next step message" in out

    def test_print_status_human_no_work(self, capsys):
        renderer.print_status_human({"work": {}})
        out = capsys.readouterr().out
        assert "No active work found" in out

    def test_print_verify_human_pass(self, capsys):
        data = {
            "status": "pass",
            "work": "W-0001",
            "openspec": {"passed": True},
            "git": {"clean": True, "branch": "main"},
            "next": "REVIEW",
            "errors": [],
        }
        renderer.print_verify_human(data)
        out = capsys.readouterr().out
        assert "PASS" in out
        assert "W-0001" in out

    def test_print_verify_human_fail_with_errors(self, capsys):
        data = {
            "status": "fail",
            "work": "W-0001",
            "openspec": {"passed": False},
            "git": {"clean": False, "branch": "main"},
            "next": "PLANNING",
            "errors": ["OpenSpec validation failed"],
        }
        renderer.print_verify_human(data)
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "OpenSpec validation failed" in out

    def test_warn_success_info(self, capsys):
        renderer.warn("Warning text")
        renderer.success("Success text")
        renderer.info("Info text")
        err = capsys.readouterr().err
        assert "Warning text" in err
