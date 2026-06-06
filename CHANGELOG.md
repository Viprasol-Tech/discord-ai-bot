# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-01

### Added
- `LLM` abstract base class with deterministic offline `FakeLLM` and `EchoLLM`
  implementations.
- `ConversationStore` — bounded per-channel conversation memory with optional
  system prompt.
- `CommandRouter` — parses `!ask` / `/ask` style commands with aliases and
  dispatch to handlers.
- `RateLimiter` — per-key token-bucket limiter with an injectable clock.
- `BotCore.handle_message()` — network-free orchestration tying router, memory,
  rate limiter and LLM together.
- Optional `DiscordRuntime` adapter that lazily imports `discord.py` for live
  use; installable via the `discord` extra.
- Terminal chat simulator (`python -m discord_ai_bot`) and a runnable
  `examples/demo.py`.
- Tooling: ruff, mypy (strict), pytest, multi-OS GitHub Actions CI, Docker,
  Dependabot, and full project documentation.

[Unreleased]: https://github.com/Viprasol-Tech/discord-ai-bot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Viprasol-Tech/discord-ai-bot/releases/tag/v0.1.0
