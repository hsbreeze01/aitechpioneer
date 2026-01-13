import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(title="Test API with CORS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def simple_background_task(message: str):
    logger.info(f"[CORS] Background task executed: {message}")

@app.get("/")
async def root():
    return {"message": "Test API with CORS"}

@app.get("/test-background")
async def test_background(background_tasks: BackgroundTasks):
    logger.info("[CORS] About to add background task...")
    background_tasks.add_task(simple_background_task, "Test message")
    logger.info("[CORS] Background task added successfully")
    return {"message": "Background task added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
