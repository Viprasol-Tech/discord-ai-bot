"""The network-free bot core.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

:class:`BotCore` is the heart of the bot and has zero dependency on
``discord.py``. It wires together the command router, conversation memory, rate
limiter and LLM into a single :meth:`BotCore.handle_message` entry point that
takes a plain :class:`IncomingMessage` and returns a :class:`BotReply`. Because
everything it needs is injected, the whole pipeline runs and is tested offline.
"""

from __future__ import annotations

from dataclasses import dataclass

from discord_ai_bot.llm import LLM, LLMError
from discord_ai_bot.memory import ConversationStore
from discord_ai_bot.ratelimit import RateLimiter
from discord_ai_bot.router import CommandRouter


@dataclass(frozen=True, slots=True)
class IncomingMessage:
    """A normalised inbound message, independent of any chat platform.

    Attributes:
        channel_id: Identifier of the channel the message arrived on.
        author_id: Identifier of the message author.
        author_name: Display name of the author.
        content: The raw message text.
        is_bot: Whether the author is itself a bot (such messages are ignored).
    """

    channel_id: str
    author_id: str
    author_name: str
    content: str
    is_bot: bool = False


@dataclass(frozen=True, slots=True)
class BotReply:
    """The bot's decision about an incoming message.

    Attributes:
        text: The reply to send, or ``None`` when the bot stays silent.
        handled: ``True`` if the message produced any action at all.
        reason: Machine-readable outcome tag, useful for logging and tests
            (one of ``"command"``, ``"llm"``, ``"ignored_bot"``,
            ``"ignored_empty"``, ``"rate_limited"``, ``"llm_error"``).
    """

    text: str | None
    handled: bool
    reason: str

    @property
    def should_send(self) -> bool:
        """Whether there is actually text to send back to the channel."""
        return self.text is not None


class BotCore:
    """Network-free orchestration of router, memory, rate limiter and LLM.

    Args:
        llm: The completion backend to route plain messages to.
        store: Per-channel conversation memory. A default unbounded-ish store
            (cap 20) is created when omitted.
        router: Command router. A default router is created when omitted and the
            built-in ``help``/``reset`` commands are registered on it.
        rate_limiter: Optional limiter keyed by author id. When omitted, no
            throttling is applied.
        rate_limit_message: Text returned when a message is throttled.
        respond_to_bots: When ``False`` (default) messages from other bots are
            ignored to avoid feedback loops.
    """

    #: Command names that clear the channel's conversation memory.
    _RESET_COMMANDS = frozenset({"reset", "clear", "forget"})
    #: Command names that route their argument text to the LLM.
    _ASK_COMMANDS = frozenset({"ask", "chat"})

    def __init__(
        self,
        llm: LLM,
        *,
        store: ConversationStore | None = None,
        router: CommandRouter | None = None,
        rate_limiter: RateLimiter | None = None,
        rate_limit_message: str = "You're going too fast - please slow down a moment.",
        respond_to_bots: bool = False,
    ) -> None:
        """Initialise the core; see the class docstring for argument details."""
        self.llm = llm
        self.store = store if store is not None else ConversationStore(max_messages=20)
        self.rate_limiter = rate_limiter
        self.rate_limit_message = rate_limit_message
        self.respond_to_bots = respond_to_bots
        if router is None:
            router = CommandRouter()
            self._install_default_commands(router)
        self.router = router

    def _install_default_commands(self, router: CommandRouter) -> None:
        def _help(_: object) -> str:
            lines = ["Available commands:"]
            for spec in router.commands():
                lines.append(f"  !{spec.name} - {spec.help}" if spec.help else f"  !{spec.name}")
            lines.append("  !reset - Clear this channel's conversation memory")
            lines.append("Or just talk to me and I'll reply.")
            return "\n".join(lines)

        router.register("help", _help, help="Show this help message", aliases=("commands",))
        router.register("ping", lambda _: "pong", help="Health check; replies 'pong'")

    def handle_message(self, message: IncomingMessage) -> BotReply:
        """Process one inbound message and decide how to respond.

        The pipeline is: ignore bots/empties -> apply rate limiting -> try the
        command router -> otherwise record the turn and ask the LLM, storing the
        assistant reply back into memory.
        """
        if message.is_bot and not self.respond_to_bots:
            return BotReply(text=None, handled=False, reason="ignored_bot")

        content = message.content.strip()
        if not content:
            return BotReply(text=None, handled=False, reason="ignored_empty")

        if self.rate_limiter is not None and not self.rate_limiter.allow(message.author_id):
            return BotReply(text=self.rate_limit_message, handled=True, reason="rate_limited")

        prompt = content
        command = self.router.parse(content)
        if command is not None:
            if command.name in self._RESET_COMMANDS:
                self.store.clear(message.channel_id)
                return BotReply(text="Conversation memory cleared.", handled=True, reason="command")
            if command.name in self._ASK_COMMANDS:
                # !ask / /ask routes the remaining text straight to the LLM.
                if not command.args:
                    return BotReply(
                        text="Ask me something, e.g. `!ask How do I center a div?`",
                        handled=True,
                        reason="command",
                    )
                prompt = command.args
            else:
                command_reply = self.router.dispatch(content)
                if command_reply is not None:
                    return BotReply(text=command_reply, handled=True, reason="command")
                # Unknown prefix command: treat the whole text as chat.

        self.store.add_user(message.channel_id, prompt, author=message.author_name)
        try:
            reply = self.llm.complete(self.store.history(message.channel_id))
        except LLMError as exc:
            return BotReply(
                text=f"Sorry, I couldn't generate a reply: {exc}",
                handled=True,
                reason="llm_error",
            )
        self.store.add_assistant(message.channel_id, reply)
        return BotReply(text=reply, handled=True, reason="llm")
