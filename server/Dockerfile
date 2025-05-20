# server/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY server.py .
EXPOSE 8082

CMD ["python", "server.py", "--port", "8080"]
