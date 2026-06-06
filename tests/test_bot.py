from collections.abc import Sequence

from discord_ai_bot.bot import BotCore, IncomingMessage
from discord_ai_bot.llm import LLM, FakeLLM, LLMError
from discord_ai_bot.memory import ConversationStore, Message
from discord_ai_bot.ratelimit import RateLimiter


def msg(content: str, *, author_id: str = "u1", is_bot: bool = False) -> IncomingMessage:
    return IncomingMessage(
        channel_id="c1",
        author_id=author_id,
        author_name="alice",
        content=content,
        is_bot=is_bot,
    )


def test_end_to_end_chat_with_fake_llm():
    core = BotCore(llm=FakeLLM(scripted={"hi": "hello back"}))
    reply = core.handle_message(msg("hi"))
    assert reply.reason == "llm"
    assert reply.text == "hello back"
    assert reply.should_send is True


def test_conversation_is_remembered_across_turns():
    core = BotCore(llm=FakeLLM(), store=ConversationStore(max_messages=10))
    core.handle_message(msg("first"))
    core.handle_message(msg("second"))
    history = core.store.history("c1")
    contents = [m.content for m in history if m.role == "user"]
    assert contents == ["first", "second"]
    # assistant replies were stored too
    assert any(m.role == "assistant" for m in history)


def test_ask_command_routes_args_to_llm():
    core = BotCore(llm=FakeLLM(scripted={"weather?": "sunny"}))
    reply = core.handle_message(msg("!ask weather?"))
    assert reply.text == "sunny"
    # stored prompt is the args, not the raw command
    assert core.store.history("c1")[-2].content == "weather?"


def test_ask_without_args_prompts_user():
    core = BotCore(llm=FakeLLM())
    reply = core.handle_message(msg("!ask"))
    assert reply.reason == "command"
    assert "Ask me something" in (reply.text or "")


def test_help_command_lists_commands():
    core = BotCore(llm=FakeLLM())
    reply = core.handle_message(msg("!help"))
    assert reply.reason == "command"
    assert "ping" in (reply.text or "")


def test_ping_command():
    core = BotCore(llm=FakeLLM())
    assert core.handle_message(msg("!ping")).text == "pong"


def test_reset_command_clears_memory():
    core = BotCore(llm=FakeLLM())
    core.handle_message(msg("remember this"))
    assert core.store.count("c1") > 0
    reply = core.handle_message(msg("!reset"))
    assert reply.reason == "command"
    assert core.store.count("c1") == 0


def test_bot_messages_are_ignored():
    core = BotCore(llm=FakeLLM())
    reply = core.handle_message(msg("hi", is_bot=True))
    assert reply.reason == "ignored_bot"
    assert reply.should_send is False


def test_empty_messages_are_ignored():
    core = BotCore(llm=FakeLLM())
    reply = core.handle_message(msg("    "))
    assert reply.reason == "ignored_empty"


def test_rate_limiting_blocks_after_capacity():
    rl = RateLimiter(capacity=2, refill_rate=0.0001)
    core = BotCore(llm=FakeLLM(), rate_limiter=rl)
    assert core.handle_message(msg("1")).reason == "llm"
    assert core.handle_message(msg("2")).reason == "llm"
    blocked = core.handle_message(msg("3"))
    assert blocked.reason == "rate_limited"
    assert blocked.should_send is True


def test_rate_limit_is_per_author():
    rl = RateLimiter(capacity=1, refill_rate=0.0001)
    core = BotCore(llm=FakeLLM(), rate_limiter=rl)
    assert core.handle_message(msg("a", author_id="alice")).reason == "llm"
    assert core.handle_message(msg("b", author_id="alice")).reason == "rate_limited"
    assert core.handle_message(msg("c", author_id="bob")).reason == "llm"


def test_llm_error_is_surfaced_gracefully():
    class BrokenLLM(LLM):
        name = "broken"

        def complete(self, history: Sequence[Message]) -> str:
            raise LLMError("backend down")

    core = BotCore(llm=BrokenLLM())
    reply = core.handle_message(msg("hi"))
    assert reply.reason == "llm_error"
    assert "couldn't generate" in (reply.text or "")
