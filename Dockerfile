# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rest.py .

RUN mkdir -p /app/logs

ENV LOG_LEVEL=INFO
ENV PORT=5000
ENV WELCOME_MESSAGE="Welcome to the custom app"

EXPOSE 5000

CMD ["python", "rest.py"]