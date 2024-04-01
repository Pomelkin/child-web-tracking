import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64

app = FastAPI()


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


# manager = ConnectionManager()
def process_img(data: str):
    data_b64 = data.encode("utf-8")
    img_data = base64.b64decode(data_b64)
    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), 2)
    _, img_encoded = cv2.imencode(".jpg", img)
    jpg_as_txt = base64.b64encode(img_encoded).decode("utf-8")
    return jpg_as_txt


active_connections = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            encoded_jpg = await asyncio.to_thread(process_img, data)
            await websocket.send_text(encoded_jpg)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
