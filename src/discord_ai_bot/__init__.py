"""Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

A Discord AI bot whose core is fully decoupled from ``discord.py``: it routes
user messages to a pluggable LLM and replies, with per-channel conversation
memory, command parsing, and token-bucket rate limiting. The core runs and is
tested entirely offline (no network, no bot token) thanks to a deterministic
:class:`~discord_ai_bot.llm.FakeLLM`. A thin, lazily-imported runtime adapter
connects the same core to a live Discord gateway when you want it.
"""

from __future__ import annotations

from discord_ai_bot.bot import BotCore, BotReply
from discord_ai_bot.llm import LLM, EchoLLM, FakeLLM, LLMError
from discord_ai_bot.memory import ConversationStore, Message
from discord_ai_bot.ratelimit import RateLimiter
from discord_ai_bot.router import Command, CommandRouter, CommandSpec

__all__ = [
    "LLM",
    "BotCore",
    "BotReply",
    "Command",
    "CommandRouter",
    "CommandSpec",
    "ConversationStore",
    "EchoLLM",
    "FakeLLM",
    "LLMError",
    "Message",
    "RateLimiter",
    "__version__",
]

__version__ = "0.1.0"
