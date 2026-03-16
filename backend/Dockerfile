FROM python:3.12-slim

WORKDIR /app

COPY _requirements.txt requirements.txt
COPY _env .env
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8200
