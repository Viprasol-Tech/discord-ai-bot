from discord_ai_bot.cli import build_core, main, run_session
from discord_ai_bot.llm import FakeLLM


def test_run_session_replies_to_each_line():
    core = build_core(llm=FakeLLM(scripted={"hi": "hey"}))
    out = list(run_session(["hi", "!ping"], core))
    assert out == ["hey", "pong"]


def test_run_session_skips_silent_turns():
    core = build_core()
    out = list(run_session(["   "], core))  # empty -> no reply
    assert out == []


def test_version_flag_exits_zero(capsys):
    code = 0
    try:
        main(["--version"])
    except SystemExit as exc:
        code = exc.code or 0
    captured = capsys.readouterr()
    assert "discord-ai-bot" in captured.out
    assert code == 0


def test_live_without_token_errors(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    assert main(["--live"]) == 2
