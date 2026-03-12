FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy EVERYTHING in the backend folder (api, runner, etc.)
COPY backend/ .

# Ensure profile setup without baking in private data
RUN if [ ! -f profile.json ]; then cp profile.json.template profile.json; fi

EXPOSE 8000

# The Start Command (Pointing to Salim's main entry point)
CMD ["uvicorn", "api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]