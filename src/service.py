from concurrent.futures import ThreadPoolExecutor
from multiprocessing.connection import Connection
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.shared import shared_values
import asyncio


async def handle_users_frames(
    websocket: WebSocket, img_converter_conn: Connection, num: int
):
    lock = shared_values["lock"]
    workers = shared_values["detection_workers"]

    with ThreadPoolExecutor(max_workers=1) as executor:
        loop = asyncio.get_running_loop()
        while True:
            try:
                base64_img = await websocket.receive_text()
                await loop.run_in_executor(
                    executor, img_converter_conn.send, base64_img
                )
                img = await loop.run_in_executor(executor, img_converter_conn.recv)
                # img_converter_conn.send(base64_img)
                # img = img_converter_conn.recv()

                detection_worker_lock = None
                detection_worker_conn = None
                async with lock:
                    for worker in workers:
                        worker_lock = worker["lock"]
                        if not worker_lock.locked():
                            detection_worker_conn = worker["connection"]
                            detection_worker_lock = worker_lock
                            break

                if detection_worker_lock is None:
                    continue

                async with detection_worker_lock:
                    await loop.run_in_executor(
                        executor, detection_worker_conn.send, (0, img)
                    )
                    results = await loop.run_in_executor(
                        executor, detection_worker_conn.recv
                    )

                await websocket.send_text(results)
            except WebSocketDisconnect:
                await loop.run_in_executor(executor, img_converter_conn.close)
                break
    return
