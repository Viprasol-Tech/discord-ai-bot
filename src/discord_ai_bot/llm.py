"""LLM abstraction layer.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

This module defines the :class:`LLM` abstract base class that every model
backend must implement, plus two deterministic, offline implementations used for
local development and the test suite:

* :class:`FakeLLM` -- replays scripted answers (and a deterministic fallback) so
  tests are fully reproducible without any network access or API keys.
* :class:`EchoLLM` -- a trivial backend that echoes the latest user turn, handy
  for smoke-testing the wiring end to end.

A real provider (OpenAI, Anthropic, a local model, ...) only has to subclass
:class:`LLM` and implement :meth:`LLM.complete`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from discord_ai_bot.memory import Message


class LLMError(RuntimeError):
    """Raised when an LLM backend fails to produce a completion."""


class LLM(ABC):
    """Abstract base class for chat completion backends.

    Implementations receive the rolling conversation history (oldest first) and
    return a single assistant reply. They must be safe to call repeatedly and
    should raise :class:`LLMError` on failure rather than leaking backend
    specific exceptions.
    """

    #: Human-readable backend name, surfaced in logs and the CLI banner.
    name: str = "llm"

    @abstractmethod
    def complete(self, history: Sequence[Message]) -> str:
        """Return an assistant reply for the given conversation ``history``.

        Args:
            history: Conversation turns, oldest first. The final element is the
                most recent user message the model should respond to.

        Returns:
            The assistant's reply text.

        Raises:
            LLMError: If the backend cannot produce a completion.
        """
        raise NotImplementedError


class FakeLLM(LLM):
    """Deterministic offline LLM for tests and local demos.

    The model first looks for a scripted answer keyed by the (lower-cased,
    stripped) latest user message. If none is found it returns a deterministic
    fallback that echoes the prompt and reports how many turns of context it
    received, so assertions stay stable across runs.
    """

    name = "fake"

    def __init__(self, scripted: dict[str, str] | None = None) -> None:
        """Initialise the backend.

        Args:
            scripted: Optional mapping of normalised user text to canned
                replies. Keys are matched case-insensitively after stripping
                surrounding whitespace.
        """
        self._scripted = {k.strip().lower(): v for k, v in (scripted or {}).items()}

    def complete(self, history: Sequence[Message]) -> str:
        """Return a scripted or deterministic reply for ``history``."""
        if not history:
            raise LLMError("cannot complete an empty conversation")
        last = history[-1]
        key = last.content.strip().lower()
        if key in self._scripted:
            return self._scripted[key]
        turns = len(history)
        return f"[fake-llm] You said: {last.content!r} (context: {turns} turn(s))"


class EchoLLM(LLM):
    """Trivial backend that echoes back the most recent user message."""

    name = "echo"

    def complete(self, history: Sequence[Message]) -> str:
        """Return the latest user message verbatim."""
        if not history:
            raise LLMError("cannot complete an empty conversation")
        return history[-1].content
