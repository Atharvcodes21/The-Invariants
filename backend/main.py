import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, consultations, analytics

app = FastAPI(title="VoiceRx Sync API", version="2.0.0")

# CORS — set ALLOWED_ORIGINS in env as comma-separated URLs
# e.g. "https://voicerx.onrender.com,http://localhost:3000"
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,          prefix="/api/auth",          tags=["auth"])
app.include_router(consultations.router, prefix="/api/consultations",  tags=["consultations"])
app.include_router(analytics.router,     prefix="/api/analytics",      tags=["analytics"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "VoiceRx Sync API"}
