FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt update && apt upgrade -y && apt install libusb-1.0-0

COPY pyproject.toml .python-version README.md /app/

RUN uv sync

COPY ./src /app/src
