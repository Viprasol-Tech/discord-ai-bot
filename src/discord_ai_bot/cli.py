"""Terminal chat simulator.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

A small REPL that drives the exact same :class:`~discord_ai_bot.bot.BotCore`
used in production, but entirely offline against the deterministic
:class:`~discord_ai_bot.llm.FakeLLM`. It lets you exercise commands, memory and
rate limiting from the terminal without a Discord token. With ``--live`` and a
``DISCORD_TOKEN`` it instead launches the real gateway adapter.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable, Iterator

from discord_ai_bot import __version__
from discord_ai_bot.bot import BotCore, IncomingMessage
from discord_ai_bot.llm import LLM, FakeLLM
from discord_ai_bot.memory import ConversationStore
from discord_ai_bot.ratelimit import RateLimiter

_BANNER = (
    "Discord AI Bot by Viprasol Tech - offline simulator\n"
    "Type a message and press Enter. Try !help, !ask <q>, !reset. Ctrl-D to quit."
)


def build_core(llm: LLM | None = None) -> BotCore:
    """Build a :class:`BotCore` with sensible offline defaults."""
    return BotCore(
        llm=llm if llm is not None else FakeLLM(),
        store=ConversationStore(max_messages=20, system_prompt="You are a helpful assistant."),
        rate_limiter=RateLimiter(capacity=5, refill_rate=1.0),
    )


def run_session(lines: Iterable[str], core: BotCore | None = None) -> Iterator[str]:
    """Feed ``lines`` through a core and yield each reply line.

    This is the testable heart of the simulator: it has no I/O of its own, so
    the test suite can drive a whole conversation and assert on the replies.
    """
    bot = core if core is not None else build_core()
    for line in lines:
        reply = bot.handle_message(
            IncomingMessage(
                channel_id="cli",
                author_id="local-user",
                author_name="you",
                content=line,
            )
        )
        if reply.should_send and reply.text is not None:
            yield reply.text


def _repl(core: BotCore) -> int:
    print(_BANNER)
    try:
        while True:
            try:
                line = input("you> ")
            except EOFError:
                print()
                break
            for out in run_session([line], core):
                print(f"bot> {out}")
    except KeyboardInterrupt:
        print()
    return 0


def _run_live() -> int:
    token = os.environ.get("DISCORD_TOKEN", "")
    if not token:
        print("error: DISCORD_TOKEN is not set; cannot start the live bot.", file=sys.stderr)
        return 2
    try:
        from discord_ai_bot.runtime import DiscordRuntime
    except ImportError:
        print(
            "error: discord.py is not installed. Install with "
            '`pip install "discord-ai-bot[discord]"`.',
            file=sys.stderr,
        )
        return 2
    DiscordRuntime(build_core()).run(token)
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(
        prog="discord-ai-bot",
        description="Offline Discord AI bot simulator (and optional live runner).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run the real Discord gateway adapter (needs DISCORD_TOKEN and the [discord] extra).",
    )
    args = parser.parse_args(argv)
    if args.live:
        return _run_live()
    return _repl(build_core())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
