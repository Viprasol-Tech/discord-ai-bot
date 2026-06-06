# syntax=docker/dockerfile:1

# --- Build stage: install the package and the optional discord runtime ---
FROM python:3.12-slim AS build
WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install --prefix=/install ".[discord]"

# --- Runtime stage: minimal image with a non-root user ---
FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=build /install /usr/local

RUN useradd --create-home --uid 10001 botuser
USER botuser

# Provide DISCORD_TOKEN at runtime, e.g.:
#   docker run --rm -e DISCORD_TOKEN=xxxx viprasol/discord-ai-bot
ENTRYPOINT ["discord-ai-bot"]
