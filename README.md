# SDCC's Project

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=matt-merman_SDCC&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=matt-merman_SDCC)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=matt-merman_SDCC&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=matt-merman_SDCC)

## Specification

The aim is to implement two election distributed algorithms (i.e. _Chang and Roberts algorithm_, _Bully algorithm_). Furthermore, the following services must be implemented:

- Register service;
- Heartbeat monitoring service;
- Logging information service;

>To deploy the application should be used _Docker_ containers on _EC2_ instance.

## Running

For the local execution are required [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/). Furthermore, a _requirements.txt_ file has been defined to install all the python external libraries:

```bash
# to execute in SDCC/sdcc/
pip install -r requirements.txt
```

### Local without Docker Containers

A _config.json_ (in _SDCC/sdcc_) file has been defined to manage all network settings (i.e., IP addresses, port numbers). To display the options set:

```bash
python3 run.py -h
```

Firstly you make running the register node:

```bash
# to execute in SDCC/sdcc/register. The -v flag provides a verbose execution (i.e., all messages received and sent are shown)
python3 run.py -v -c ../config.json
```

A single node can be executed as:

```bash
# to execute in SDCC/sdcc/node. Without the '-a bully' option node runs the ring-based alg.
python3 run.py -v -a bully -c ../config.json
```

#### Tests

Test execution can be handled as:

```python
# to execute in SDCC/sdcc
sudo python3 run_tests.py
```

### AWS EC2 instance with Docker Containers

[Ansible](https://docs.ansible.com/) service is used to automate the Docker installation and to copy the application code.

```bash
# To check the ec2 instance (optional)
ansible -i hosts.ini -m ping all

# To execute ansible in SDCC/sdcc/ansible
ansible-playbook -v -i hosts.ini deploy.yaml

# Connect to the EC2 instance
ssh -i "SDCC_key.pem" ubuntu@ip_instance

# To execute the whole application
sudo docker-compose up
```

## Implementation

Please see [report](https://github.com/matt-merman/SDCC/blob/main/docs/report.pdf) for more details.