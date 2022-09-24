# SDCC's Project

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=matt-merman_SDCC&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=matt-merman_SDCC)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=matt-merman_SDCC&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=matt-merman_SDCC)

## Specification

The aim is to implement two election distributed algorithms (i.e. _Chang and Roberts algorithm_, _Bully algorithm_). Furthermore the following services must be implemented:

- Register service;
- Heartbeat monitoring service;
- Logging information service;

>To deploy the application should be used _Docker_ containers on _EC2_ instance.

## Running

For the local execution are required [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/). Furthermore a _requirements.txt_ file has been defined to install all the python external libraries:

```bash
# to execute in SDCC/sdcc/
pip install -r requirements.txt
```

### Local without Docker Containers

A _config.json_ (in _SDCC/sdcc_) file has been defined to manage all network settings (i.e., ip addresses, port numbers). Firstly you make running the register node:

```bash
# to execute in SDCC/sdcc/register. The -v flag provides a verbose execution (i.e., all messages received and sent are showed)
python3 run.py -v -c ../config.json
```

A single node can be executed as:

```bash
# to execute in SDCC/sdcc/node. Without '-a bully' option node runs the ring-based alg.
python3 run.py -v -a bully -c ../config.json
```

#### Tests

Test execution can be handled as:

```python
# to execute in SDCC/sdcc
sudo python3 run_tests.py
```

### Local with Docker Containers

A _docker-compose.yml_ file has been defined to runs docker images (described in _Dockerfile_ files).

```bash
# to execute in SDCC/sdcc. To build the images
sudo docker-compose build                                       

# to execute in SDCC/sdcc. To run containers
sudo docker-compose up --no-recreate

# to execute in SDCC/sdcc. To remove images created
sudo docker system prune -a
```

### AWS EC2 with Docker Containers

```bash
# Connect to EC2 instances
ssh -i "SDCC_key.pem" ubuntu@ip_instance

# Upload application to EC2 instance
scp -i SDCC_key.pem -r SDCC/sdcc user@ip_instance:/home/user/  

# Once have access to the instance, to execute the whole application
sudo docker-compose up
```

## Implementation

Please see [report](https://github.com/matt-merman/SDCC/blob/main/docs/report.pdf) for more details.