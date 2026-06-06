import pytest

from discord_ai_bot.memory import ConversationStore, Message


def test_add_and_history_roundtrip():
    store = ConversationStore(max_messages=10)
    store.add_user("c1", "hello", author="alice")
    store.add_assistant("c1", "hi there")
    history = store.history("c1")
    assert [m.role for m in history] == ["user", "assistant"]
    assert history[0].content == "hello"
    assert history[0].author == "alice"


def test_history_is_capped_at_max_messages():
    store = ConversationStore(max_messages=3)
    for i in range(6):
        store.add_user("c1", f"msg-{i}")
    history = store.history("c1")
    assert len(history) == 3
    assert [m.content for m in history] == ["msg-3", "msg-4", "msg-5"]


def test_system_prompt_is_prepended_and_not_counted():
    store = ConversationStore(max_messages=2, system_prompt="be nice")
    store.add_user("c1", "a")
    store.add_user("c1", "b")
    store.add_user("c1", "c")  # evicts "a"
    history = store.history("c1")
    assert history[0] == Message(role="system", content="be nice")
    assert [m.content for m in history[1:]] == ["b", "c"]
    assert store.count("c1") == 2  # system prompt excluded from count


def test_channels_are_isolated():
    store = ConversationStore()
    store.add_user("c1", "in one")
    store.add_user("c2", "in two")
    assert store.count("c1") == 1
    assert store.count("c2") == 1
    assert store.history("c1")[0].content == "in one"


def test_clear_forgets_channel():
    store = ConversationStore()
    store.add_user("c1", "hi")
    store.clear("c1")
    assert store.count("c1") == 0
    assert store.history("c1") == []


def test_non_positive_max_rejected():
    with pytest.raises(ValueError, match="must be positive"):
        ConversationStore(max_messages=0)
