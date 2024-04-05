from asyncio import AbstractEventLoop
from contextlib import asynccontextmanager

# from asyncio import Lock
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import asyncio
import multiprocessing as mp
from multiprocessing import Lock
from concurrent.futures import ProcessPoolExecutor
from ultralytics import YOLO
from src.models import Stream
from queue import Full
import torch

ml_models = {}
shared_values = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    manager = mp.Manager()
    ml_models["yolo"] = YOLO("yolov8n.pt")
    shared_values["lock"] = manager.Lock()
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)

active_connections = []


def process_img(base64_img: str, model: YOLO, lock: Lock) -> list[list[int]]:
    print(torch.cuda.is_available())
    bytes_img = base64.b64decode(base64_img)
    arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
    img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)

    with lock:
        results = model.predict(img)

    boxes = []
    for bboxes in results[0].boxes.data.tolist():
        x1, y1, x2, y2, _, _ = bboxes
        boxes.append([x1, y1, x2, y2])
    return boxes


async def detection(websocket: WebSocket, model: YOLO, lock: Lock):
    assert id(lock) == id(shared_values["lock"])
    assert id(model) == id(ml_models["yolo"])

    with ProcessPoolExecutor(max_workers=1) as pool:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        while True:
            base64_img = await websocket.receive_text()
            boxes = await loop.run_in_executor(
                pool, process_img, base64_img, model, lock
            )

            await websocket.send_json({"bboxes": boxes})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    model = ml_models["yolo"]
    model.to("cuda")
    model_lock = shared_values["lock"]

    try:
        while True:
            await detection(websocket, model, model_lock)
    except WebSocketDisconnect:
        print("disconnected")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
