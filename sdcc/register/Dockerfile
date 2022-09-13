# sudo docker build -t register-image .  
# sudo docker run --net host register-image
# or in sdcc/
#   sudo docker-compose up
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

