# Dockerized 3-Tier Search Service with FastAPI & Elasticsearch

![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?logo=elasticsearch&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?logo=google-cloud&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

This repository contains the implementation of a 3-tier, containerized search application. The project demonstrates core software engineering and MLOps principles, including containerization with Docker, building a microservices-style architecture, and deployment on a cloud platform (GCP) managed entirely via the command-line interface.

The application consists of a FastAPI frontend, a FastAPI backend API, and an Elasticsearch database, each running in its own isolated Docker container.

## Core Concepts & Key Features

-   **Containerization with Docker:** Each component of the 3-tier application is containerized using optimized, production-ready Dockerfiles.
-   **Multi-Tier Architecture:** A classic system design featuring a separate frontend, backend, and database to ensure scalability and separation of concerns.
-   **Docker Networking:** A custom bridge network was configured to enable secure and efficient communication between the frontend and backend containers, while isolating the database.
-   **Data Persistence:** Docker volumes are used for the Elasticsearch container to ensure that the indexed data persists even if the container is stopped or removed.
-   **Cloud Deployment & CLI Management:** The entire environment was set up and managed on Google Cloud Platform (GCP) using only the command-line interface, showcasing proficiency in a headless server environment.
-   **Image Optimization:** Focused on creating lightweight and secure Docker images using industry best practices.

## System Architecture

The diagram below illustrates the high-level architecture, showing the interaction between the user, the frontend, the backend, and the Elasticsearch database container across two virtual machines.

![Architecture Diagram](https://github.com/user-attachments/assets/77aff3ad-2ba3-4fc0-a5ba-6f8ad567cde8)


## Tech Stack

-   **Frontend:** FastAPI (serving an HTML/CSS/JS page)
-   **Backend:** FastAPI, Python
-   **Database:** Elasticsearch
-   **DevOps & Cloud:** Docker, Docker Compose, Google Cloud Platform (GCP)

## Repository Structure
```
.
├───Dockerfiles
│   ├───Task1
│   │   └───frontend
│   ├───Task2
│   │   └───backend
│   └───Task3
│       ├───elasticsearch
│       └───setup
├───lab08-backend
│   ├───backend
│   ├───elasticsearch
│   └───setup
└───lab08-frontend
    └───frontend
        └───templates
```
