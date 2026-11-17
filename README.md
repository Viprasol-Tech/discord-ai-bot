<p align="center"><img src="docs/assets/logo.png" width="120"></p>

# Discord AI Bot

**A Python Discord AI bot that routes messages to an LLM and replies — with a clean core fully decoupled from `discord.py`, so it runs and tests without a network or a bot token.**

*Built and maintained by [Viprasol Tech](https://viprasol.com) — Fintech Experts. Full-Stack Builders.*

<p align="center">
  <a href="https://github.com/Viprasol-Tech/discord-ai-bot/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Viprasol-Tech/discord-ai-bot/ci.yml?branch=main&style=flat-square" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square" alt="Python versions">
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/code%20style-ruff-261230?style=flat-square" alt="Code style: ruff"></a>
  <a href="https://t.me/viprasol_help"><img src="https://img.shields.io/badge/Telegram-viprasol__help-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Telegram"></a>
  <a href="https://github.com/Viprasol-Tech/discord-ai-bot/stargazers"><img src="https://img.shields.io/github/stars/Viprasol-Tech/discord-ai-bot?style=flat-square" alt="Stars"></a>
</p>

---

## ✨ Features

- 🧠 **LLM-agnostic core** — a tiny `LLM` ABC; bring OpenAI, Anthropic, a local model, or the bundled `FakeLLM`.
- 🔌 **Decoupled from `discord.py`** — the whole core runs and is tested with no network and no bot token.
- 🧪 **Deterministic `FakeLLM`** — scripted, reproducible replies make the test suite fast and offline.
- 💬 **Per-channel conversation memory** — bounded history per channel keeps prompts small and predictable.
- 🧭 **Command router** — parses both `!ask` and `/ask` styles, with aliases and a built-in help command.
- 🚦 **Token-bucket rate limiting** — per-user throttling with an injectable clock for deterministic tests.
- 🧩 **One clean entry point** — `BotCore.handle_message()` ties router, memory, limiter and LLM together.
- 🛰️ **Optional live adapter** — a lazily-imported `discord.py` runtime; install it only when you go live.
- 🖥️ **Terminal simulator** — chat with the bot from your shell, offline, via `python -m discord_ai_bot`.
- 🛠️ **Strict tooling** — ruff, mypy `--strict`, pytest, multi-OS CI, Docker, and full docs.

## 🚀 Quickstart

### Docker

```bash
docker build -t discord-ai-bot .
docker run --rm -it discord-ai-bot          # offline terminal simulator
```

### Native (Python 3.11+)

```bash
git clone https://github.com/Viprasol-Tech/discord-ai-bot.git
cd discord-ai-bot
python -m pip install -e ".[dev]"

# Try it offline — no token needed:
python -m discord_ai_bot
python examples/demo.py
```

To run a live bot, install the optional adapter and provide a token:

```bash
python -m pip install -e ".[discord]"
cp .env.example .env        # then edit DISCORD_TOKEN
export DISCORD_TOKEN=...     # or set it in your environment / secret manager
python -m discord_ai_bot --live
```

## 🧑‍💻 Usage

The core is plain Python — no Discord required:

```python
from discord_ai_bot import BotCore, ConversationStore, FakeLLM, RateLimiter
from discord_ai_bot.bot import IncomingMessage

core = BotCore(
    llm=FakeLLM(scripted={"who built you?": "Viprasol Tech — https://viprasol.com"}),
    store=ConversationStore(max_messages=20, system_prompt="You are a helpful assistant."),
    rate_limiter=RateLimiter(capacity=5, refill_rate=1.0),
)

reply = core.handle_message(
    IncomingMessage(
        channel_id="general",
        author_id="user-1",
        author_name="Ada",
        content="!ask who built you?",
    )
)
print(reply.text)  # -> "Viprasol Tech — https://viprasol.com"
```

Plug in a real model by subclassing the `LLM` ABC:

```python
from collections.abc import Sequence
from discord_ai_bot.llm import LLM
from discord_ai_bot.memory import Message


class MyLLM(LLM):
    name = "my-provider"

    def complete(self, history: Sequence[Message]) -> str:
        # call your provider with `history`, return the reply text
        ...
```

## 🏗️ Architecture

| Component | Module | Responsibility |
|-----------|--------|----------------|
| `LLM` ABC + `FakeLLM`/`EchoLLM` | `llm.py` | Pluggable completion backend; deterministic offline ones for tests |
| `ConversationStore` | `memory.py` | Bounded per-channel history (+ optional system prompt) |
| `CommandRouter` | `router.py` | Parse `!`/`/` commands, dispatch to handlers |
| `RateLimiter` | `ratelimit.py` | Per-key token bucket with injectable clock |
| `BotCore` | `bot.py` | Ties it all together via `handle_message()` — **no `discord.py`** |
| `DiscordRuntime` | `runtime.py` | Optional, lazily-imported live gateway adapter |
| CLI | `cli.py` | Offline terminal simulator and `--live` launcher |

## 🗺️ Roadmap

- [ ] Streaming/typing-indicator support in the live adapter
- [ ] Native slash-command (application command) registration
- [ ] Persistent conversation store backends (SQLite / Redis)
- [ ] Per-guild configuration and prompt templates
- [ ] First-class OpenAI / Anthropic LLM adapters
- [ ] Tool/function-calling hooks

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our
[Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR. Security issues? See
[SECURITY.md](SECURITY.md).

## 📬 Contact — Viprasol Tech Private Limited

- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

> *Viprasol Tech — fintech software, algorithmic trading systems, MT4/MT5 bots, AI voice agents, and B2B SaaS. Need a custom build? [Get in touch](mailto:support@viprasol.com).*

## 📄 License

Released under the [MIT License](LICENSE) — © 2025 Viprasol Tech Private Limited.
