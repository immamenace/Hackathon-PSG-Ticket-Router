from fastapi import FastAPI
from m1_mvr.router import router as mvr_router
from m2_advanced.router import router as advanced_router

app = FastAPI(
    title="Smart-Support Ticket Routing Engine",
    description="Hackathon Challenge: High-throughput, intelligent routing engine for SaaS support tickets.",
    version="1.0.0"
)

# Mount the routers for different milestones
app.include_router(mvr_router)
app.include_router(advanced_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Ticket Routing Engine is running"}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the server from the project root!
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
