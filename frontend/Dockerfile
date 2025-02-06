FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install --yes build-essential curl > /dev/null

COPY ../frontend ./frontend
COPY ../pyproject.toml ../poetry.lock ./

# Copy the README.md file
COPY ../README.md ./

# Copy the shared_utils directory
COPY ../shared_utils ./shared_utils

RUN pip install poetry
RUN poetry install --with streamlit --without dev --no-interaction --no-ansi

HEALTHCHECK CMD curl --fail http://localhost:8081/_stcore/health

ENTRYPOINT ["poetry", "run", "python", "-m", "streamlit", "run", "frontend/app/main.py", "--server.port=8081", "--server.address=0.0.0.0"]
