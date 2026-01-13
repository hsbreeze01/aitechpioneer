import logging
import time
from fastapi import FastAPI, BackgroundTasks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Async Background Tasks Test")

async def async_background_task(message: str, delay: int = 2):
    logger.info(f"[ASYNC BACKGROUND] Starting task: {message}")
    await asyncio.sleep(delay)
    logger.info(f"[ASYNC BACKGROUND] Completed task: {message} (after {delay}s)")

import asyncio

@app.get("/")
async def root():
    return {"message": "Async Background Tasks Test API"}

@app.get("/test-async-background")
async def test_async_background(background_tasks: BackgroundTasks):
    logger.info("[ASYNC] About to add async background task...")
    background_tasks.add_task(async_background_task, "async background task", 2)
    logger.info("[ASYNC] Async background task added successfully")
    return {"message": "Async background task added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
