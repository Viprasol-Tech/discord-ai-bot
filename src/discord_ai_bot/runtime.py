"""Optional live Discord gateway adapter.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

This module is the *only* place that touches ``discord.py``, and it imports it
lazily inside :meth:`DiscordRuntime.run` so the rest of the package (and the
whole test suite) works with neither the dependency nor a bot token installed.
Install the runtime with::

    pip install "discord-ai-bot[discord]"

The adapter is intentionally thin: it converts a ``discord.Message`` into the
platform-neutral :class:`~discord_ai_bot.bot.IncomingMessage`, hands it to the
injected :class:`~discord_ai_bot.bot.BotCore`, and sends back the reply.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord_ai_bot.bot import BotCore, IncomingMessage

if TYPE_CHECKING:  # pragma: no cover - typing only, no runtime import
    import discord


class DiscordRuntime:
    """Connects a :class:`BotCore` to the live Discord gateway.

    Args:
        core: The network-free bot core that decides on replies.
        require_mention: When ``True`` the bot only responds in guild channels
            if it is mentioned (direct messages always get a reply). Commands
            (messages starting with a known prefix) are always processed.
    """

    def __init__(self, core: BotCore, *, require_mention: bool = False) -> None:
        """Initialise the adapter; see the class docstring for argument details."""
        self.core = core
        self.require_mention = require_mention

    def _build_client(self) -> discord.Client:
        import discord  # lazy import: only needed for live runs

        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        core = self.core
        require_mention = self.require_mention

        async def on_message(msg: Any) -> None:
            if client.user is not None and msg.author.id == client.user.id:
                return

            is_dm = msg.guild is None
            mentioned = client.user is not None and client.user in getattr(msg, "mentions", [])
            is_command = core.router.parse(msg.content) is not None
            if require_mention and not (is_dm or mentioned or is_command):
                return

            incoming = IncomingMessage(
                channel_id=str(msg.channel.id),
                author_id=str(msg.author.id),
                author_name=msg.author.display_name,
                content=_strip_mention(msg, client.user),
                is_bot=bool(getattr(msg.author, "bot", False)),
            )
            reply = core.handle_message(incoming)
            if reply.should_send and reply.text is not None:
                await msg.channel.send(reply.text)

        client.event(on_message)
        return client

    def run(self, token: str) -> None:
        """Connect to Discord and block, processing messages until stopped.

        Args:
            token: A Discord bot token. Never hard-code this; load it from the
                ``DISCORD_TOKEN`` environment variable or a secret manager.

        Raises:
            ValueError: If ``token`` is empty.
        """
        if not token:
            raise ValueError("a non-empty Discord bot token is required")
        client = self._build_client()
        client.run(token)


def _strip_mention(msg: Any, me: Any) -> str:
    """Remove a leading bot mention from the message content, if present."""
    content: str = msg.content
    if me is None:
        return content
    for token in (f"<@{me.id}>", f"<@!{me.id}>"):
        if content.startswith(token):
            return content[len(token) :].strip()
    return content
