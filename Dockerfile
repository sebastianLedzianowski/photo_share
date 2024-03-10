FROM python:3.11

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . /app

ENV RUNNING_IN_DOCKER=true

CMD ["/root/.cache/pypoetry/virtualenvs/photoshare-BS01HZAn-py3.11/bin/gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]