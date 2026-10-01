FROM python:3.13-alpine

WORKDIR /app
COPY src/gitea_exporter.py /app/gitea_exporter.py

EXPOSE 9178
ENTRYPOINT ["python3", "/app/gitea_exporter.py"]
