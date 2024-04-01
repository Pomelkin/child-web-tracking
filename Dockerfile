FROM python:3.12
LABEL authors="emely"

RUN addgroup --gid 10001 apiuser && \
    adduser --uid 10001 --gid 10001 --disabled-password --gecos "" papperuser

WORKDIR /src/data/app

COPY  requirements.txt requirements.txt
RUN apt-get update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm requirements.txt

COPY --chown=apiuser:apiuser . .

USER apiuser

ENTRYPOINT ["uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8080"]

