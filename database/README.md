This project uses Docker to simplify environment and dependency management. It includes a Dockerfile for creating a custom Docker image and a docker-compose.yml file for orchestrating containers.

## Prerequisites

Ensure that Docker and Docker Compose are installed on your machine. You can download Docker here and Docker Compose here.

Project Structure

    •	Dockerfile : File used to build the Docker image.
    •	docker-compose.yml : Configuration file to orchestrate containers.

## Installation

Build the Docker image:

```bash
docker build -t my-postgres-pgvector .
```

Start the containers:

```bash
docker-compose up -d
```

This command will build the image from the Dockerfile and start the services defined in docker-compose.yml.
