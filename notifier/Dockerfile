FROM python:3.10.14-slim-bullseye

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y wget && \
    pip install --no-cache-dir requests psycopg2-binary && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x wait-for-it.sh

CMD ["python", "main.py"]
