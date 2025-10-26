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

# Keep a simple HTTP server alive AND run the bot every 6 hours
# INTERVAL_SECONDS can override the 6h interval via env
CMD ["/bin/sh", "-lc", "python -m http.server 8080 & while true; do echo 'Running job at' $(date); python -u main.py || true; sleep ${INTERVAL_SECONDS:-21600}; done"]

# Keep the container alive as a simple HTTP server (no code changes needed)
CMD ["python", "-m", "http.server", "8080"]
