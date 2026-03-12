FROM python:3.12-slim

# 1. Install system dependencies and add Google's Repo
RUN apt-get update && apt-get install -y wget gnupg curl unzip --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python requirements (Pointing to the backend folder)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the backend code
COPY backend/ .

# 4. Fallback for profile data
RUN if [ ! -f profile.json ]; then cp profile.json.template profile.json; fi

EXPOSE 8000

# 5. Start command
CMD ["uvicorn", "api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]