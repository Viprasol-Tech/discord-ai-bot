"""Per-channel conversation memory.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

The :class:`ConversationStore` keeps a bounded, in-memory history of messages
per Discord channel. Bounding the history keeps prompts small and predictable
and stops a long-lived channel from growing without limit.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    """A single conversation turn.

    Attributes:
        role: Who produced the message -- ``"system"``, ``"user"`` or
            ``"assistant"``.
        content: The message text.
        author: Optional display name of the human author (for user turns).
    """

    role: Role
    content: str
    author: str | None = None


class ConversationStore:
    """Bounded per-channel message history.

    Each channel keeps at most ``max_messages`` of the most recent turns. An
    optional ``system_prompt`` is always prepended to the history returned by
    :meth:`history`, but it does not count against the per-channel cap.
    """

    def __init__(self, max_messages: int = 20, system_prompt: str | None = None) -> None:
        """Initialise the store.

        Args:
            max_messages: Maximum number of stored turns per channel. Must be a
                positive integer.
            system_prompt: Optional system message prepended to every channel's
                history.

        Raises:
            ValueError: If ``max_messages`` is not positive.
        """
        if max_messages <= 0:
            raise ValueError("max_messages must be positive")
        self._max = max_messages
        self._system = Message(role="system", content=system_prompt) if system_prompt else None
        self._channels: dict[str, deque[Message]] = defaultdict(self._new_deque)

    def _new_deque(self) -> deque[Message]:
        return deque(maxlen=self._max)

    def add(self, channel_id: str, message: Message) -> None:
        """Append ``message`` to ``channel_id``'s history, evicting the oldest."""
        self._channels[channel_id].append(message)

    def add_user(self, channel_id: str, content: str, author: str | None = None) -> Message:
        """Record a user turn and return the stored :class:`Message`."""
        msg = Message(role="user", content=content, author=author)
        self.add(channel_id, msg)
        return msg

    def add_assistant(self, channel_id: str, content: str) -> Message:
        """Record an assistant turn and return the stored :class:`Message`."""
        msg = Message(role="assistant", content=content)
        self.add(channel_id, msg)
        return msg

    def history(self, channel_id: str) -> list[Message]:
        """Return the channel's history (system prompt first, if configured)."""
        turns = list(self._channels.get(channel_id, ()))
        if self._system is not None:
            return [self._system, *turns]
        return turns

    def clear(self, channel_id: str) -> None:
        """Forget all stored turns for ``channel_id``."""
        self._channels.pop(channel_id, None)

    def count(self, channel_id: str) -> int:
        """Return the number of stored turns for ``channel_id`` (excludes system)."""
        return len(self._channels.get(channel_id, ()))
