# Experiments API
This is a simple API for managing experiments and teams. It is built using FastAPI and SQLAlchemy, using PostgreSQL database. The whole application is containerized using Docker.

## Installation
To run the application, you need to have [Docker](https://docs.docker.com/get-docker/) installed on your machine. Once installed, follow the steps below to run the application:
1. Clone the repository
2. Run `docker compose up` to build the images and run the containers
3. The API will be available at `http://localhost:8000`
4. The documentation will be available at `http://localhost:8000/docs`

## API endpoints

The details related to API endpoints are available in the documentation provided by Swagger and integrated with FastAPI. You can access it at `http://localhost:8000/docs`. There are several more endpoints than reqired, to enable full CRUD operations for both experiments and teams.

## Running tests
The tests are written using Pytest. To run the tests, run:

```
docker compose exec web pytest
```

## Areas to improve
- Add more tests to cover more edge cases - due to time issues, the current tests are really basic and do not cover all possible scenarios, neither check all the responses' data
- Expand logging - the current logging is not sufficient and could be improved to provide more information about the application's behavior
- Add more detailed validation