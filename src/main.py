from asyncio import AbstractEventLoop
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from ultralytics import YOLO
from src.models import Stream
from queue import Full

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["yolo"] = YOLO("yolov8n.pt")
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)

active_connections = []


async def receiving_messages(websocket: WebSocket, queue: asyncio.Queue):
    base64_img = await websocket.receive_text()
    try:
        queue.put_nowait(base64_img)
    except asyncio.QueueFull:
        pass


def process_img(base64_img: str) -> list[list]:
    bytes_img = base64.b64decode(base64_img)
    arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
    img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)

    model = ml_models["yolo"]
    results = model.predict(img)

    if len(results[0]) == 0:
        return []

    boxes = []
    for bboxes in results[0].boxes.data.tolist():
        x1, y1, x2, y2, _, _ = bboxes
        boxes.append([x1, y1, x2, y2])
    return boxes


async def detection(websocket: WebSocket, queue: mp.Queue):
    while True:
        base64_img = await queue.get()
        with ProcessPoolExecutor() as pool:
            loop: AbstractEventLoop = asyncio.get_event_loop()
            results = loop.run_in_executor(pool, process_img, base64_img)
            bboxes = await results
        await websocket.send_json({"bboxes": bboxes})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue()
    detection_task = asyncio.create_task(detection(websocket, queue))
    try:
        while True:
            await receiving_messages(websocket, queue)
    except WebSocketDisconnect:
        detection_task.cancel()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
