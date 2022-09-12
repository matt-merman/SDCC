# to build the image: 
#   sudo docker build -t register-image .
# to execute an instance:
#   sudo docker run register-image
# to delete all containers:
#   sudo systemctl restart docker.service
#   reboot

# syntax=docker/dockerfile:1
FROM node:12-alpine
RUN apk add --no-cache python3
WORKDIR /register
#EXPOSE 1234
COPY . . 
CMD ["python3", "run.py", "-v"]

