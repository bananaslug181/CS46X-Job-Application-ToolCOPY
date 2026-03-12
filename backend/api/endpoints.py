from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import application_runner  # This is the file we fixed earlier!

app = FastAPI(title="Job Hunting AI Tool API")

# Define what the incoming data looks like
class ApplicationRequest(BaseModel):
    job_url: str
    profile_data: Dict[str, Any]

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "Job Hunting AI Tool"}

@app.post("/run")
async def run_application(request: ApplicationRequest):
    """
    This is the route the frontend is calling.
    It takes the data and hands it off to the Selenium runner.
    """
    try:
        # We call the 'run' function from application_runner.py
        result = application_runner.run(
            job_url=request.job_url,
            profile_data=request.profile_data,
            headless=True # Always True for Railway!
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}