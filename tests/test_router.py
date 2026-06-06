import pytest

from discord_ai_bot.router import CommandRouter


def make_router() -> CommandRouter:
    router = CommandRouter()
    router.register("ask", lambda c: f"asked:{c.args}", help="ask")
    router.register("ping", lambda c: "pong", aliases=("p",))
    return router


def test_parses_bang_prefix():
    router = make_router()
    cmd = router.parse("!ask how are you")
    assert cmd is not None
    assert cmd.name == "ask"
    assert cmd.args == "how are you"
    assert cmd.raw == "!ask how are you"


def test_parses_slash_prefix():
    cmd = make_router().parse("/ping")
    assert cmd is not None
    assert cmd.name == "ping"
    assert cmd.args == ""


def test_command_name_is_lowercased():
    cmd = make_router().parse("!ASK Hello")
    assert cmd is not None
    assert cmd.name == "ask"
    assert cmd.args == "Hello"


def test_plain_message_is_not_a_command():
    assert make_router().parse("just chatting") is None


def test_prefix_followed_by_space_is_not_a_command():
    assert make_router().parse("! not a command") is None


def test_bare_prefix_is_not_a_command():
    assert make_router().parse("!") is None


def test_dispatch_runs_handler():
    assert make_router().dispatch("!ask hi") == "asked:hi"


def test_dispatch_alias_resolves_to_same_handler():
    assert make_router().dispatch("!p") == "pong"


def test_dispatch_unknown_command_returns_none():
    assert make_router().dispatch("!nope") is None


def test_dispatch_non_command_returns_none():
    assert make_router().dispatch("hello there") is None


def test_duplicate_registration_raises():
    router = make_router()
    with pytest.raises(ValueError, match="already registered"):
        router.register("ask", lambda c: "x")


def test_commands_are_deduped_over_aliases():
    names = [s.name for s in make_router().commands()]
    assert names == ["ask", "ping"]


def test_empty_prefixes_rejected():
    with pytest.raises(ValueError, match="at least one prefix"):
        CommandRouter(prefixes=())
