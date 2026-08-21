FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# never bake a local dev DB into the image: always start from a clean seed
RUN rm -rf /app/data && mkdir -p /app/data

# bind to whatever the platform injects (Render sets PORT); local default 8000
ENV PORT=8000 \
    DEV_MODE=true

EXPOSE 8000

CMD ["sh", "-c", "python seed.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
