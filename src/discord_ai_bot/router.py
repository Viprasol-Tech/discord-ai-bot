"""Command parsing and routing.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

The :class:`CommandRouter` parses a raw message into a :class:`Command` and
dispatches it to a registered handler. It understands the classic ``!ask`` style
prefix commands as well as ``/ask`` slash-style commands, so the same router
works for both message events and (text rendered) slash interactions.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

#: Signature of a command handler: it receives the parsed command and returns
#: the reply text to send back to the channel.
Handler = Callable[["Command"], str]


@dataclass(frozen=True, slots=True)
class Command:
    """A parsed command.

    Attributes:
        name: The command name without its prefix, lower-cased (e.g. ``"ask"``).
        args: The remainder of the message after the command name, stripped.
        raw: The original, untouched message text.
    """

    name: str
    args: str
    raw: str


@dataclass(slots=True)
class CommandSpec:
    """Registration record for a single command.

    Attributes:
        name: Canonical command name (without prefix).
        handler: Callable invoked when the command matches.
        help: Short one-line description shown by the built-in ``help`` command.
        aliases: Alternative names that also resolve to this command.
    """

    name: str
    handler: Handler
    help: str = ""
    aliases: tuple[str, ...] = field(default_factory=tuple)


class CommandRouter:
    """Parses and dispatches prefix/slash commands.

    Args:
        prefixes: Iterable of accepted command prefixes. Defaults to ``!`` and
            ``/`` so both ``!ask`` and ``/ask`` are recognised.
    """

    def __init__(self, prefixes: tuple[str, ...] = ("!", "/")) -> None:
        """Initialise the router with the accepted command ``prefixes``."""
        if not prefixes:
            raise ValueError("at least one prefix is required")
        self._prefixes = prefixes
        self._specs: dict[str, CommandSpec] = {}

    def register(
        self,
        name: str,
        handler: Handler,
        *,
        help: str = "",
        aliases: tuple[str, ...] = (),
    ) -> None:
        """Register ``handler`` under ``name`` and any ``aliases``.

        Raises:
            ValueError: If the name or any alias is already registered.
        """
        spec = CommandSpec(name=name.lower(), handler=handler, help=help, aliases=aliases)
        for key in (spec.name, *(a.lower() for a in aliases)):
            if key in self._specs:
                raise ValueError(f"command {key!r} is already registered")
            self._specs[key] = spec

    def parse(self, text: str) -> Command | None:
        """Parse ``text`` into a :class:`Command`, or ``None`` if it isn't one.

        A message is a command only when it starts with a known prefix
        immediately followed by a non-space command name.
        """
        stripped = text.strip()
        for prefix in self._prefixes:
            if stripped.startswith(prefix) and len(stripped) > len(prefix):
                body = stripped[len(prefix) :]
                if body[0].isspace():
                    return None
                head, _, rest = body.partition(" ")
                return Command(name=head.lower(), args=rest.strip(), raw=text)
        return None

    def dispatch(self, text: str) -> str | None:
        """Parse and run ``text`` as a command.

        Returns:
            The handler's reply, or ``None`` if the text is not a command or no
            handler is registered for it.
        """
        command = self.parse(text)
        if command is None:
            return None
        spec = self._specs.get(command.name)
        if spec is None:
            return None
        return spec.handler(command)

    def commands(self) -> list[CommandSpec]:
        """Return the unique registered command specs (deduped over aliases)."""
        seen: dict[int, CommandSpec] = {}
        for spec in self._specs.values():
            seen[id(spec)] = spec
        return sorted(seen.values(), key=lambda s: s.name)
