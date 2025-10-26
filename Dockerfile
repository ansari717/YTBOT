# Dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tell Back4App we serve on 8080
EXPOSE 8080

# Keep the container alive as a simple HTTP server (no code changes needed)
CMD ["python", "-m", "http.server", "8080"]
