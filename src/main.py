from contextlib import asynccontextmanager
from asyncio import Lock, Semaphore
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import torch
from src.utils import img_converter, detection_worker
from src.service import handle_users_frames
from src.shared import shared_values
import logging


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

        worker = loop.run_in_executor(
            executor, detection_worker, child_detection_worker_conn
        )
        shared_values["detection_worker"] = {"connection": parent_detection_worker_conn}
        yield

        worker = shared_values["detection_worker"]
        worker_conn = worker["connection"]
        worker_conn.send("stop")
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
        executor: ProcessPoolExecutor = shared_values["process_executor"]
        parent_img_converter_conn, child_img_converter_conn = mp.Pipe(duplex=True)

        loop = asyncio.get_running_loop()
        loop.run_in_executor(executor, img_converter, child_img_converter_conn)

        await handle_users_frames(websocket, parent_img_converter_conn)
        parent_img_converter_conn.close()
        child_img_converter_conn.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
