FROM python:3.12-slim

# 1. Install system dependencies and Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    google-chrome-stable \
    --no-install-recommends \
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

# 5. Start the server
CMD ["uvicorn", "api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]