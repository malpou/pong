FROM python:3.13-slim

WORKDIR /code

RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry lock --no-update && poetry install --only main --no-interaction --no-ansi

COPY . .
EXPOSE 80

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]