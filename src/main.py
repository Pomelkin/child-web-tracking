from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
from src.models import Stream

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


@app.post("/frame", response_model=Stream)
async def process_frame(stream: Stream):
    data = base64.b64decode(stream.b64_frame)
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 2)
    _, img_encoded = cv2.imencode(".jpg", frame)
    encoded_frame = base64.b64encode(img_encoded).decode("utf-8")
    return Stream(b64_frame=encoded_frame)


# # manager = ConnectionManager()
# active_connections = []
#
#
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     active_connections.append(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             data_b64 = data.encode("utf-8")
#             img_data = base64.b64decode(data_b64)
#             img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
#             cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), 2)
#             _, img_encoded = cv2.imencode(".jpg", img)
#             jpg_as_txt = base64.b64encode(img_encoded).decode("utf-8")
#             await websocket.send_text(jpg_as_txt)
#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
