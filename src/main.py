from contextlib import asynccontextmanager
from asyncio import Lock
import uvicorn
from fastapi import FastAPI, WebSocket
import numpy as np
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import torch
from src.utils import img_converter, detection_worker
from src.service import handle_users_frames
from src.shared import shared_values, ml_models
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    torch.cuda.set_device(torch.device("cuda", 0))
    shared_values["detection_workers"] = None
    shared_values["lock"] = Lock()

    workers_num = settings.workers_num
    workers = []
    with ProcessPoolExecutor(max_workers=workers_num) as executor:
        loop = asyncio.get_running_loop()
        for i in range(workers_num):
            parent_detection_worker_conn, child_detection_worker_conn = mp.Pipe()

            worker = loop.run_in_executor(
                executor, detection_worker, child_detection_worker_conn
            )

            workers.append({"connection": parent_detection_worker_conn, "lock": Lock()})

        shared_values["detection_workers"] = workers
        yield

        for worker in workers:
            worker_conn = worker["connection"]
            worker_conn.send("stop")
    # Clean up the ML models and release the resources
    ml_models.clear()
    shared_values.clear()


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    parent_img_converter_conn, child_img_converter_conn = mp.Pipe(duplex=True)

    with ProcessPoolExecutor(max_workers=1) as pool:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(pool, img_converter, child_img_converter_conn)

        await handle_users_frames(
            websocket, parent_img_converter_conn, np.random.randint(0, 1000)
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000)
