from concurrent.futures import ThreadPoolExecutor
from multiprocessing.connection import Connection
from fastapi import WebSocket, WebSocketDisconnect
from src.shared import shared_values
from src.schemas import DetectionTaskResponse, DetectionTaskRequest
import asyncio


async def handle_users_frames(websocket: WebSocket, img_converter_conn: Connection):
    lock = shared_values["lock"]
    worker: dict = shared_values["detection_worker"]

    with ThreadPoolExecutor(max_workers=1) as executor:
        loop = asyncio.get_running_loop()
        while True:
            try:
                json_data = await websocket.receive_json()
                data = DetectionTaskRequest(**json_data)

                await loop.run_in_executor(
                    executor, img_converter_conn.send, data.base64_img
                )
                img = await loop.run_in_executor(executor, img_converter_conn.recv)

                async with lock:
                    await loop.run_in_executor(
                        executor, worker["connection"].send, (data.task, img)
                    )
                    results: DetectionTaskResponse = await loop.run_in_executor(
                        executor, worker["connection"].recv
                    )

                await websocket.send_json(results.model_dump_json())
                # await websocket.send_json(results.model_dump_json())
            except WebSocketDisconnect:
                await loop.run_in_executor(executor, img_converter_conn.close)
                break
    return
