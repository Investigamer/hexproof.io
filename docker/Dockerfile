# UV Docker / Multi-Stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

# Install project dependencies
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy files
COPY . /app/.

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    set -eux; \
    uv sync --locked --no-dev; \
    uv add gunicorn;

# Switch to final image without uv
FROM python:3.12-slim-bookworm

# Copy application from the builder, add project to path
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# Update, install and configure system dependencies, move and format entrypoint
RUN set -eux; \
	apt-get update && apt-get install -y --no-install-recommends dos2unix; \
    mv /app/docker/entrypoint.sh /app/entrypoint.sh;  \
    rm -rd docker; \
    chmod +x /app/entrypoint.sh && dos2unix /app/entrypoint.sh; \
    apt-get purge -y dos2unix; \
	rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--reload", "--workers", "4", "--timeout", "60"]
