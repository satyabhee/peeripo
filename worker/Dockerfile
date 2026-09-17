# build context must be the repo root (see docker-compose.yml), since this
# needs files from both backend/ and worker/
FROM python:3.12-slim
WORKDIR /app
COPY worker/requirements.txt worker/requirements.txt
RUN pip install --no-cache-dir -r worker/requirements.txt
COPY backend/app backend/app
COPY worker worker
CMD ["python", "-m", "worker.scheduler"]
