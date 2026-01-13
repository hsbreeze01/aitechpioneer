import logging
import time
from fastapi import FastAPI, BackgroundTasks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Background Tasks Test")

def background_task(message: str, delay: int = 2):
    logger.info(f"[BACKGROUND] Starting task: {message}")
    time.sleep(delay)
    logger.info(f"[BACKGROUND] Completed task: {message} (after {delay}s)")

@app.get("/")
async def root():
    return {"message": "Background Tasks Test API"}

@app.get("/test-sync")
async def test_sync():
    logger.info("[SYNC] Starting synchronous task")
    background_task("sync task", 1)
    logger.info("[SYNC] Completed synchronous task")
    return {"message": "Sync task completed"}

@app.get("/test-background")
async def test_background(background_tasks: BackgroundTasks):
    logger.info("[ASYNC] About to add background task...")
    background_tasks.add_task(background_task, "background task", 2)
    logger.info("[ASYNC] Background task added successfully")
    return {"message": "Background task added"}

@app.get("/test-multiple")
async def test_multiple(background_tasks: BackgroundTasks):
    logger.info("[MULTIPLE] Adding multiple background tasks...")
    for i in range(3):
        background_tasks.add_task(background_task, f"task-{i}", 1)
    logger.info("[MULTIPLE] Multiple background tasks added")
    return {"message": "Multiple background tasks added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
