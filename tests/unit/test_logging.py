"""Unit tests for logging system following AAA pattern."""

import logging

from driftless.logging import get_logger, setup_logging


class TestLogging:
    def test_get_logger_returns_named_child_logger(self):
        # Arrange & Act
        logger = get_logger("domain")

        # Assert
        assert logger.name == "driftless.domain"

    def test_setup_logging_configures_file_handler_when_driftless_dir_exists(
        self, tmp_path
    ):
        # Arrange
        driftless_dir = tmp_path / ".driftless"
        driftless_dir.mkdir()

        # Act
        setup_logging(verbose=False, repo_root=tmp_path)

        # Assert
        root_logger = logging.getLogger("driftless")
        file_handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        assert (driftless_dir / "driftless.log").exists()

    def test_setup_logging_handles_file_handler_exception(self, tmp_path, mocker):
        # Arrange
        driftless_dir = tmp_path / ".driftless"
        driftless_dir.mkdir()
        mocker.patch(
            "logging.FileHandler", side_effect=PermissionError("Read-only file system")
        )

        # Act & Assert (Should pass gracefully)
        setup_logging(verbose=False, repo_root=tmp_path)

        root_logger = logging.getLogger("driftless")
        file_handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 0

    def test_setup_logging_configures_console_handler_when_verbose(self, tmp_path):
        # Arrange & Act
        setup_logging(verbose=True, repo_root=tmp_path)

        # Assert
        root_logger = logging.getLogger("driftless")
        console_handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) >= 1

    def test_setup_logging_configures_console_handler_when_driftless_debug_env_var_set(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        monkeypatch.setenv("DRIFTLESS_DEBUG", "1")

        # Act
        setup_logging(verbose=False, repo_root=tmp_path)

        # Assert
        root_logger = logging.getLogger("driftless")
        console_handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) >= 1
