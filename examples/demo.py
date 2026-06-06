"""Runnable offline demo of the Discord AI Bot core.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

Run it with::

    python examples/demo.py

It drives a short scripted conversation through :class:`BotCore` using the
deterministic :class:`FakeLLM`, showing commands, per-channel memory and
rate limiting -- all without a Discord token or any network access.
"""

from __future__ import annotations

from discord_ai_bot import (
    BotCore,
    ConversationStore,
    FakeLLM,
    RateLimiter,
)
from discord_ai_bot.bot import IncomingMessage


def main() -> None:
    core = BotCore(
        llm=FakeLLM(scripted={"who built you?": "Viprasol Tech did - https://viprasol.com"}),
        store=ConversationStore(max_messages=10, system_prompt="You are a helpful assistant."),
        rate_limiter=RateLimiter(capacity=3, refill_rate=1.0),
    )

    script = [
        "!help",
        "Hello there!",
        "!ask who built you?",
        "!ping",
        "!reset",
    ]

    for line in script:
        reply = core.handle_message(
            IncomingMessage(
                channel_id="general",
                author_id="demo-user",
                author_name="Demo",
                content=line,
            )
        )
        print(f"you> {line}")
        if reply.should_send:
            print(f"bot> {reply.text}\n")
        else:
            print(f"bot> (silent, reason={reply.reason})\n")


if __name__ == "__main__":
    main()
