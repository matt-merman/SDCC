# sudo docker build -t node-image .  
# sudo docker run --net host node-image
# or in sdcc/
#   sudo docker-compose up

# syntax=docker/dockerfile:1
FROM node:12-alpine
RUN apk add --no-cache python3
WORKDIR /node
#EXPOSE 4321
COPY . . 
CMD ["python3", "run.py", "-v"]

