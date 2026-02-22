from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from m1_mvr.router import router as mvr_router
from m2_advanced.router import router as advanced_router
from m3_orchestrator.router import router as orchestrator_router

app = FastAPI(
    title="Smart-Support Ticket Routing Engine",
    description="Hackathon Challenge: High-throughput, intelligent routing engine for SaaS support tickets.",
    version="3.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount the routers for different milestones
app.include_router(mvr_router)
app.include_router(advanced_router)
app.include_router(orchestrator_router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the frontend UI"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Ticket Routing Engine is running"}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the server from the project root!
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
