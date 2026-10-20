import runpy
from pathlib import Path

TVCTL = Path(__file__).parents[1] / "tools/tvctl"


def load_tvctl():
    return runpy.run_path(str(TVCTL))


def test_remote_command_preserves_argument_boundaries():
    compose_remote_command = load_tvctl()["compose_remote_command"]

    assert compose_remote_command(["printf", "%s\\n", "two words"]) == (
        "printf '%s\\n' 'two words'"
    )


def test_single_remote_command_string_is_preserved():
    compose_remote_command = load_tvctl()["compose_remote_command"]
    command = 'printf "%s\\n" "$PATH" | head -n 1'

    assert compose_remote_command([command]) == command
