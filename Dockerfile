FROM python:3.12-slim

# Install system tools for scanning
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsutils \
    whois \
    openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE ${PORT}

CMD gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 app:app
