FROM python:3.12-slim

# 1. Install system dependencies and add Google's Repo (Modern Method)
RUN apt-get update && apt-get install -y wget gnupg curl unzip --no-install-recommends \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the backend code
COPY backend/ .

# 4. Fallback for profile data
RUN if [ ! -f profile.json ]; then cp profile.json.template profile.json; fi

EXPOSE 8000

# 5. Start command
CMD ["uvicorn", "api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]