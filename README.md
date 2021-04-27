# Backend API of Dicery

Dicery is a dice-rolling app where a group of friends can roll the dice and have their dice results broadcasted to everyone else. Built with the FastAPI framework, SSE-Starlette and `encode/broadcaster`, the API receives requests to:

- create a room
- add members to a room
- close a room
- broadcast dice results to users subscribed in a room using Server-Sent Events

## Running the API locally

1. Install Docker
2. Run `docker-compose up`
