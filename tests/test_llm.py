import pytest

from discord_ai_bot.llm import EchoLLM, FakeLLM, LLMError
from discord_ai_bot.memory import Message


def test_fake_llm_uses_scripted_answer_case_insensitively():
    llm = FakeLLM(scripted={"Hello": "Hi!"})
    reply = llm.complete([Message(role="user", content="  hello  ")])
    assert reply == "Hi!"


def test_fake_llm_deterministic_fallback_mentions_turns():
    llm = FakeLLM()
    out = llm.complete(
        [
            Message(role="user", content="a"),
            Message(role="assistant", content="b"),
            Message(role="user", content="why?"),
        ]
    )
    assert "why?" in out
    assert "3 turn" in out


def test_fake_llm_is_deterministic():
    llm = FakeLLM()
    history = [Message(role="user", content="same")]
    assert llm.complete(history) == llm.complete(history)


def test_echo_llm_returns_last_user_message():
    assert EchoLLM().complete([Message(role="user", content="repeat me")]) == "repeat me"


def test_empty_history_raises():
    for llm in (FakeLLM(), EchoLLM()):
        with pytest.raises(LLMError):
            llm.complete([])
