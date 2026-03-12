FROM python:3.12-slim

# 1. Install Chrome (Modern GPG method)
RUN apt-get update && apt-get install -y wget gnupg curl unzip --no-install-recommends \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. THE FIX: Set the Python Path so it can see the 'tests' folder
ENV PYTHONPATH=/app

# 3. Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy everything
COPY backend/ .

# 5. Fallback for profile data
RUN if [ ! -f profile.json ]; then cp profile.json.template profile.json; fi

EXPOSE 8000

# 6. Use shell form to ensure $PORT is used correctly
CMD uvicorn api.endpoints:app --host 0.0.0.0 --port ${PORT:-8000}