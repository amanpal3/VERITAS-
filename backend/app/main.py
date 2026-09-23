"""
VERITAS - Main FastAPI Entrypoint
Initializes application, CORS middleware, Sentry error monitoring, and router registration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VERITAS Criminal Network Intelligence API",
    version="1.0.0",
    description="AI-powered graph analytics and intelligence system for law enforcement."
)

# Placeholder for route inclusion and middleware configuration
