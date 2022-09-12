# to build the image: 
#   sudo docker build -t node-image .
# to execute an instance:
#   sudo docker run -it node-image
# or in sdcc/
#   sudo docker-compose up

# syntax=docker/dockerfile:1
FROM node:12-alpine
RUN apk add --no-cache python3
WORKDIR /node
#EXPOSE 4321
COPY . . 
CMD ["python3", "run.py", "-v"]

