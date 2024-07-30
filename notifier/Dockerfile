FROM python:3.10-alpine

WORKDIR /app

COPY . /app

RUN pip install requests psycopg2-binary

CMD ["python", "main.py"]
