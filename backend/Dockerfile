FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
ARG INSTALL_DATA=false
ARG INSTALL_RESEARCH=false
RUN if [ "$INSTALL_RESEARCH" = "true" ]; then uv sync --locked --no-install-project --extra dev --extra research; elif [ "$INSTALL_DATA" = "true" ]; then uv sync --locked --no-install-project --extra dev --extra data; else uv sync --locked --no-install-project --extra dev; fi
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
