from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ml.predictor import WaterQualityPredictor
from app.routes import router as routes_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Water Quality ML API",
        version="1.0.0",
        description="Real-time water quality analysis using ML models"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change to specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routes
    app.include_router(routes_router)

    # Attach predictor instance for reuse (optional)
    app.state.predictor = WaterQualityPredictor()

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
