FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.22 /uv /uvx /bin/
WORKDIR /app
COPY . /app
ENV UV_PYTHON_DOWNLOADS=0 UV_NO_DEV=1
RUN uv sync --locked
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
