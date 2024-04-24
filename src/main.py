import asyncio
import multiprocessing as mp
from asyncio import Lock, Semaphore
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from src.service import user_frames_handler, detection_worker
from src.shared import shared_values


@asynccontextmanager
async def lifespan(app: FastAPI):
    # logger = mp.log_to_stderr()
    # logger.setLevel(mp.SUBDEBUG)

    mp.set_start_method("spawn")
    cores = mp.cpu_count()
    torch.cuda.set_device(torch.device("cuda", 0))

    shared_values["detection_worker"] = None
    shared_values["process_executor"] = None
    shared_values["semaphore"] = Semaphore(cores - 2)
    shared_values["lock"] = Lock()

    with ProcessPoolExecutor(max_workers=cores - 1) as executor:
        shared_values["process_executor"] = executor

        loop = asyncio.get_running_loop()
        parent_detection_worker_conn, child_detection_worker_conn = mp.Pipe()

        worker_task = loop.run_in_executor(
            executor, detection_worker, child_detection_worker_conn
        )

        shared_values["detection_worker"] = {
            "worker_task": worker_task,
            "connection": parent_detection_worker_conn,
        }
        yield

        worker = shared_values["detection_worker"]
        worker_conn = worker["connection"]
        worker_conn.close()
    # Clean up the ML models and release the resources
    shared_values.clear()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    semaphore: Semaphore = shared_values["semaphore"]
    if semaphore.locked():
        await websocket.send_text("too many users")
        await websocket.close()

    async with semaphore:
        await user_frames_handler(websocket)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
