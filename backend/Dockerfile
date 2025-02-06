FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install project dependencies
RUN poetry install --with fastapi --without dev --no-interaction --no-ansi

# Copy the FastAPI application code
COPY backend backend
COPY shared_utils shared_utils


# Expose the port the app runs on
EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/api/healthcheck

# Command to run the FastAPI app using Uvicorn
CMD ["poetry", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
