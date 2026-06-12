# TrueNorth decision engine — production image.
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the package (with the Postgres driver) plus Alembic for migrations.
COPY pyproject.toml README.md ./
COPY truenorth_engine ./truenorth_engine
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN pip install ".[postgres]" && chmod +x /usr/local/bin/entrypoint.sh

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# entrypoint runs `alembic upgrade head` then execs the CMD.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "truenorth_engine.api:app", "--host", "0.0.0.0", "--port", "8000"]
