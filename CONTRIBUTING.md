# Contributing to Discord AI Bot

Thanks for your interest in improving Discord AI Bot, maintained by
[Viprasol Tech](https://viprasol.com)! Contributions of all sizes are welcome.

## Getting started

```bash
git clone https://github.com/Viprasol-Tech/discord-ai-bot.git
cd discord-ai-bot
python -m pip install -e ".[dev]"
```

## Before you open a PR

Please make sure the full verification suite passes locally — CI runs the exact
same checks across Linux, macOS and Windows on Python 3.11–3.13:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

Run `python -m ruff format .` to auto-format your changes.

## Guidelines

- **Keep the core offline.** Anything in the core (`bot`, `llm`, `memory`,
  `router`, `ratelimit`) must not import `discord.py` or require a network. The
  only place `discord` may be imported is `runtime.py`, and it must stay a lazy
  import.
- **Add tests.** New behaviour needs offline tests using `FakeLLM`/`EchoLLM`.
- **Type everything.** The project runs `mypy --strict`; public APIs are fully
  typed and documented with Google-style docstrings.
- **Conventional commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
  `chore:`) are appreciated and keep the changelog tidy.

## Reporting bugs / requesting features

Use the issue templates under **New issue**. For security reports, see
[SECURITY.md](SECURITY.md) instead of opening a public issue.

By contributing you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
