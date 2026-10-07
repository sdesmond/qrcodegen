FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /usr/local/bin/uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_LINK_MODE=copy PATH=/opt/venv/bin:$PATH

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY qr_generator.py .
COPY presets.json .
COPY preview_app.py .
COPY gunicorn_config.py .
COPY templates/ ./templates/

RUN useradd -r -u 1001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn_config.py", "preview_app:app"]
