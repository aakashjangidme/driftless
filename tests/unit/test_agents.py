"""Unit tests for Agent Skills generator following AAA pattern."""

from driftless.agents.agents_md import AGENTS_MD_CONTENT, write_agents_skill
from driftless.agents.claude import CLAUDE_MD_CONTENT, write_claude_skill
from driftless.agents.manager import install_agent_skills


class TestClaudeSkill:
    def test_write_claude_skill_creates_new_file(self, tmp_path):
        # Arrange & Act
        path = write_claude_skill(tmp_path)

        # Assert
        assert path.exists()
        assert path.name == "CLAUDE.md"
        assert "# Driftless — AI-Native SDLC Workflow" in path.read_text(encoding="utf-8")

    def test_write_claude_skill_appends_to_existing_file_without_driftless_marker(
        self, tmp_path
    ):
        # Arrange
        target = tmp_path / "CLAUDE.md"
        target.write_text("# Existing Project Instructions\nDo something else.\n")

        # Act
        path = write_claude_skill(tmp_path, force=False)

        # Assert
        content = path.read_text(encoding="utf-8")
        assert "# Existing Project Instructions" in content
        assert "# Driftless — AI-Native SDLC Workflow" in content

    def test_write_claude_skill_returns_existing_file_when_driftless_marker_present(
        self, tmp_path
    ):
        # Arrange
        target = tmp_path / "CLAUDE.md"
        target.write_text("# Driftless — AI-Native SDLC Workflow\nAlready installed.")

        # Act
        path = write_claude_skill(tmp_path, force=False)

        # Assert
        assert (
            path.read_text(encoding="utf-8")
            == "# Driftless — AI-Native SDLC Workflow\nAlready installed."
        )

    def test_write_claude_skill_overwrites_when_force_true(self, tmp_path):
        # Arrange
        target = tmp_path / "CLAUDE.md"
        target.write_text("# Old Content")

        # Act
        path = write_claude_skill(tmp_path, force=True)

        # Assert
        assert path.read_text(encoding="utf-8") == CLAUDE_MD_CONTENT


class TestAgentsSkill:
    def test_write_agents_skill_creates_new_file(self, tmp_path):
        # Arrange & Act
        path = write_agents_skill(tmp_path)

        # Assert
        assert path.exists()
        assert path.name == "AGENTS.md"
        assert "# Driftless — AI-Native SDLC Workflow" in path.read_text(encoding="utf-8")

    def test_write_agents_skill_appends_to_existing_file_without_driftless_marker(
        self, tmp_path
    ):
        # Arrange
        target = tmp_path / "AGENTS.md"
        target.write_text("# Existing Universal Instructions\nDo something else.\n")

        # Act
        path = write_agents_skill(tmp_path, force=False)

        # Assert
        content = path.read_text(encoding="utf-8")
        assert "# Existing Universal Instructions" in content
        assert "# Driftless — AI-Native SDLC Workflow" in content

    def test_write_agents_skill_returns_existing_file_when_driftless_marker_present(
        self, tmp_path
    ):
        # Arrange
        target = tmp_path / "AGENTS.md"
        target.write_text("# Driftless — AI-Native SDLC Workflow\nAlready installed.")

        # Act
        path = write_agents_skill(tmp_path, force=False)

        # Assert
        assert (
            path.read_text(encoding="utf-8")
            == "# Driftless — AI-Native SDLC Workflow\nAlready installed."
        )

    def test_write_agents_skill_overwrites_when_force_true(self, tmp_path):
        # Arrange
        target = tmp_path / "AGENTS.md"
        target.write_text("# Old Content")

        # Act
        path = write_agents_skill(tmp_path, force=True)

        # Assert
        assert path.read_text(encoding="utf-8") == AGENTS_MD_CONTENT


class TestAgentSkillManager:
    def test_install_agent_skills_installs_both_claude_and_agents(self, tmp_path):
        # Arrange & Act
        installed = install_agent_skills(tmp_path, tools="claude")

        # Assert
        names = [p.name for p in installed]
        assert "CLAUDE.md" in names
        assert "AGENTS.md" in names

    def test_install_agent_skills_skips_when_tools_none(self, tmp_path):
        # Arrange & Act
        installed = install_agent_skills(tmp_path, tools="none")

        # Assert
        assert installed == []

    def test_install_agent_skills_handles_writer_exceptions(self, tmp_path, mocker):
        # Arrange
        mocker.patch(
            "driftless.agents.manager.write_claude_skill",
            side_effect=PermissionError("Denied"),
        )
        mocker.patch(
            "driftless.agents.manager.write_agents_skill",
            side_effect=PermissionError("Denied"),
        )

        # Act
        installed = install_agent_skills(tmp_path, tools="claude")

        # Assert
        assert installed == []
