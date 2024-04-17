import pprint
from contextlib import asynccontextmanager
from asyncio import Lock
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from ultralytics import YOLO
from queue import Full
import torch
import logging
from multiprocessing.connection import Connection
from src.pipeline import detect_action
from src.video_processing.detection.pose_estimator import PoseEstimator
from src.video_processing.detection.gesture_recognizer import GestureRecognizer
from src.video_processing.detection.hand_detector import HandDetector
import cv2

ml_models = {}
shared_values = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    torch.cuda.set_device(torch.device("cuda", 0))
    ml_models["pose_estimation"] = PoseEstimator()
    ml_models["gesture_recognizer"] = GestureRecognizer()
    ml_models["hand_detector"] = HandDetector()
    shared_values["lock"] = Lock()
    shared_values["img_processor_workers_connections"] = None

    img_processor_workers_num = 1
    img_processor_workers_connections = []
    img_processor_workers = []
    with ProcessPoolExecutor(max_workers=img_processor_workers_num) as executor:
        loop = asyncio.get_running_loop()
        for i in range(img_processor_workers_num):
            parent_img_processor_connection, child_img_processor_connection = mp.Pipe()
            task = loop.run_in_executor(
                executor, img_processor, child_img_processor_connection
            )
            img_processor_workers_connections.append(parent_img_processor_connection)
            img_processor_workers.append(img_processor)

        shared_values["img_processor_workers_connections"] = (
            img_processor_workers_connections
        )
        yield

        for worker_conn in img_processor_workers_connections:
            worker_conn.send("stop")
    # Clean up the ML models and release the resources
    ml_models.clear()
    shared_values.clear()


app = FastAPI(lifespan=lifespan)


def img_processor(connection: Connection) -> None:
    keypoints_detector = PoseEstimator()
    hand_detector = HandDetector()
    gesture_recognizer = GestureRecognizer()
    while True:
        data = connection.recv()
        if data == "stop":
            logging.info("stop img_processor")
            break
        keypoint, img = data
        results = detect_action(
            frame=img,
            keypoint_index=keypoint,
            keypoints_detector=keypoints_detector,
            hand_detector=hand_detector,
            gesture_recognizer=gesture_recognizer,
            verbose=True,
        )
        connection.send(results.model_dump_json())


def img_converter(connection: Connection) -> None:
    while True:
        data = connection.recv()
        if data == "stop":
            logging.info("stop img_preprocessor")
            break
        base64_img = data
        bytes_img = base64.b64decode(base64_img)
        arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
        img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)
        connection.send(img)
    return


async def handle_users_frame(websocket: WebSocket, img_converter_conn: Connection):
    keypoints_detector = ml_models["pose_estimation"]
    hand_detector = ml_models["hand_detector"]
    gesture_recognizer = ml_models["gesture_recognizer"]

    lock = shared_values["lock"]
    while True:
        try:
            base64_img = await websocket.receive_text()
            img_converter_conn.send(base64_img)
            img = img_converter_conn.recv()
            workers = shared_values["img_processor_workers_connections"]

            connection = workers[0]

            connection.send((0, img))
            results = connection.recv()
            print(results)
            # results = await detect_action(
            #     frame=img,
            #     keypoint_index=0,
            #     lock=lock,
            #     keypoints_detector=keypoints_detector,
            #     hand_detector=hand_detector,
            #     gesture_recognizer=gesture_recognizer,
            #     verbose=True,
            # )
            # print(results)
            # await websocket.send_json(results.model_dump_json())
        except WebSocketDisconnect:
            img_converter_conn.send("stop")
            print("disconnected")
            return


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    parent_img_converter_conn, child_img_converter_conn = mp.Pipe(duplex=True)

    with ProcessPoolExecutor(max_workers=1) as pool:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(pool, img_converter, child_img_converter_conn)

        await handle_users_frame(websocket, parent_img_converter_conn)

    parent_img_converter_conn.close()
    child_img_converter_conn.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000)
