import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from app.api.upload import router as upload_router
from app.api.query import router as query_router
from app.api.context import router as context_router
from app.api.ask import router as ask_router
from app.api.history import router as history_router
from app.api.insights import router as insights_router
from app.api.anomalies import router as anomalies_router
from app.api.visualizations import router as visualizations_router
from app.auth.router import router as auth_router


load_dotenv()


app = FastAPI(
    title="AI Data Analyst Agent",
    description="Agentic AI platform for conversational data analysis",
    version="0.1.0",
)



# CORS CONFIGURATION


frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:4200",
)

allowed_origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

if frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# API ROUTERS


app.include_router(upload_router)

app.include_router(query_router)

app.include_router(context_router)

app.include_router(ask_router)

app.include_router(history_router)

app.include_router(insights_router)

app.include_router(anomalies_router)

app.include_router(visualizations_router)

app.include_router(auth_router)


# ROOT ENDPOINT


@app.get("/")
def root():
    return {
        "message": "AI Data Analyst Agent API is running",
        "version": "0.1.0",
    }



# HEALTH CHECK


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Data Analyst Agent",
        "version": "0.1.0",
    }