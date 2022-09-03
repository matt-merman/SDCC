# to execute: 
# 1. sudo docker build -t node -f Dockerfile . --no-cache
# 2. sudo docker run -it node:latest

# syntax=docker/dockerfile:1
FROM python:3.7-alpine
WORKDIR /code
COPY requirements.txt requirements.txt
RUN apk upgrade --update && apk add --no-cache python3 python3-dev gcc gfortran freetype-dev musl-dev libpng-dev g++ lapack-dev
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY ./sdcc/node/ .
CMD ["python3", "run.py"]

