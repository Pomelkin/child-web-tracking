from asyncio import AbstractEventLoop
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from src.models import Stream
from queue import Full

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []
#
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#
#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)
#
#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)
#
#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)


# @app.post("/frame", response_model=Stream)
# async def process_frame(stream: Stream):
#     data = stream.b64_frame
#     data_b64 = data.encode("utf-8")
#     bytes_data = base64.b64decode(data_b64)
#     frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
#     cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 2)
#     _, img_encoded = cv2.imencode(".jpg", frame)
#     encoded_frame = base64.b64encode(img_encoded).decode("utf-8")
#     return Stream(b64_frame=encoded_frame)


# manager = ConnectionManager()
active_connections = []


async def receiving_messages(websocket: WebSocket, queue: asyncio.Queue):
    base64_img = await websocket.receive_text()
    try:
        queue.put_nowait(base64_img)
    except asyncio.QueueFull:
        pass


def process_img(base64_img: str) -> np.ndarray:
    bytes_img = base64.b64decode(base64_img)
    arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
    img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)
    return cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), 2)


async def detection(websocket: WebSocket, queue: mp.Queue):
    while True:
        base64_img = await queue.get()
        with ProcessPoolExecutor() as pool:
            loop: AbstractEventLoop = asyncio.get_event_loop()
            img_task = loop.run_in_executor(pool, process_img, base64_img)
            img = await img_task
        await websocket.send_json({"bboxes": [100, 100, 200, 200]})


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
