FROM python:3.11.7-slim
LABEL authors="emely"

RUN addgroup --gid 10001 apiuser && \
    adduser --uid 10001 --gid 10001 --disabled-password --gecos "" apiuser

ENV PYTHONPATH=/usr/data/app

WORKDIR /usr/data/app

COPY  requirements.txt requirements.txt
RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6  -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm requirements.txt

COPY --chown=apiuser:apiuser . .

USER apiuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

