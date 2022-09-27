# syntax=docker/dockerfile:1
FROM node:12-alpine
RUN apk add --no-cache gcc musl-dev linux-headers python3 py3-pip python3-dev
WORKDIR /register
COPY register/ .
COPY config.json .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "run.py", "-v", "-a", "bully", "-c", "./config.json"]
#CMD ["python3", "run.py", "-v", "-c", "./config.json"]

