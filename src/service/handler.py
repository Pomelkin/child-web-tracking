from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import Json
from src.utils import img_converter
from src.shared import shared_values
from src.schemas import DetectionTaskRequest
from multiprocessing.connection import Connection
import asyncio


async def user_frames_handler(websocket: WebSocket):
    lock: asyncio.Lock = shared_values["lock"]
    process_executor: ProcessPoolExecutor = shared_values["process_executor"]
    worker: dict = shared_values["detection_worker"]
    worker_task: asyncio.Future = worker["worker_task"]
    worker_conn: Connection = worker["connection"]

    with ThreadPoolExecutor(max_workers=1) as thread_executor:
        loop = asyncio.get_running_loop()
        while True:
            try:
                json_data = await websocket.receive_json()
                data = DetectionTaskRequest(**json_data)

                img = await loop.run_in_executor(
                    process_executor, img_converter, data.base64_img
                )

                async with lock:
                    await loop.run_in_executor(
                        thread_executor, worker_conn.send, (data.task, img)
                    )

                    if worker_task.done():
                        if worker_task.exception() is not None:
                            raise worker_task.exception()

                    results: Json = await loop.run_in_executor(
                        thread_executor, worker_conn.recv
                    )

                await websocket.send_json(results)
            except WebSocketDisconnect:
                break
    return
