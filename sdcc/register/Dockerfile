# sudo docker build -t node-image .  
# sudo docker run --net host node-image
# or in sdcc/
#   sudo docker-compose up

# syntax=docker/dockerfile:1
FROM node:12-alpine
RUN apk add --no-cache gcc musl-dev linux-headers python3 py3-pip python3-dev
WORKDIR /register
COPY . .
RUN pip install -r requirements.txt
EXPOSE 54350
CMD ["python3", "./register/run.py", "-v"]

