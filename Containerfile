FROM python:3.14-slim

WORKDIR /pyrig

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY README.md LICENSE pyproject.toml uv.lock ./

RUN useradd -m -u 1000 appuser

RUN chown -R appuser:appuser .

USER appuser

COPY --chown=appuser:appuser pyrig pyrig

RUN uv sync --no-group dev

RUN rm README.md LICENSE pyproject.toml uv.lock

ENTRYPOINT ["uv", "run", "pyrig"]