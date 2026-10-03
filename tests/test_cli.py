import pytest

from football_agent.cli import main


def test_cli_requires_a_command() -> None:
    with pytest.raises(SystemExit):
        main([])
