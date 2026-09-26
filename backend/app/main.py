from fastapi import FastAPI

from app.api.upload import router as upload_router


app = FastAPI(
    title="AI Data Analyst Agent",
    description="Agentic AI platform for conversational data analysis",
    version="0.1.0",
)


app.include_router(upload_router)


@app.get("/")
def root():
    return {
        "message": "AI Data Analyst Agent API is running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }