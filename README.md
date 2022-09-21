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



### AWS EC2 with Docker Containers

```bash
# Connect to EC2 instances
ssh -i "SDCC_key.pem" ubuntu@ip_instance

# Upload application to EC2 instance
scp -i SDCC_key.pem -r SDCC/sdcc user@ip_instance:/home/user/  

# Execute the whole application with nodes in local 
docker compose up
```



## Implementation

Please see [report](https://github.com/matt-merman/SDCC/blob/main/docs/report.pdf) for more details.




