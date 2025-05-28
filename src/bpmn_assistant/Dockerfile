FROM python:3.12

WORKDIR /app

# Copy pyproject.toml and uv.lock for dependency management
COPY pyproject.toml /app/
COPY uv.lock /app/

# Install uv
RUN pip install --upgrade pip
RUN pip install --no-cache-dir uv

# Copy the source code early to ensure folder structure exists for uv sync
COPY ./src/bpmn_assistant /app/src/bpmn_assistant

# Install dependencies
RUN uv sync

# Install bpmn_assistant package
RUN uv pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.bpmn_assistant.app:app", "--host", "0.0.0.0", "--port", "8000"]