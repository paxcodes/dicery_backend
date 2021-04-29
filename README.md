# Dicery (Backend API)

<p align="center">
    <a href="https://app.netlify.com/sites/jolly-clarke-ad50df/deploys"><img src="https://api.netlify.com/api/v1/badges/0d2d516e-be66-482f-8d35-b743f7c1c34e/deploy-status" alt="Netlify Status"/></a>
    <a href="https://app.buddy.works/paxmargret/dicery-backend/pipelines/pipeline/321588"><img src="https://app.buddy.works/paxmargret/dicery-backend/pipelines/pipeline/321588/badge.svg?token=4b2a7bd16f0c58f0eaa34f27824a709c73c4ea73cce5810e7fc62916ba745d3f" alt="buddy pipeline" /></a>
</p>

<p align="center"><em>
Dicery is a dice-rolling app where a group of friends can create their own room, roll the dice, and have their dice results broadcasted to everyone in the same room. 
</em></p>

<p align="center">
    <img src="https://user-images.githubusercontent.com/13646646/94694372-9f689980-02e9-11eb-9582-2f5d20bc95a2.gif" alt="Dicery App" />
<p>

<p align="center">
    Frontend Github Repository: <a href="https://github.com/paxcodes/dicery_app">paxcodes/dicery_app</a>
</p>

<p align="center">
Built with <a href="https://github.com/tiangolo/fastapi">FastAPI</a> | Deployed in an AWS EC2 instance using principles in <a href="https://dockerswarm.rocks/">dockerswarm.rocks</a> | <br /> CI/CD using <a href="https://buddy.works">buddy.works</a>
</p>

## About

The API receives requests to:

- create a room
- add members to a room
- close a room
- broadcast dice results to users subscribed in a room using Server-Sent Events

## Development

To setup a development environment:

1. Install [Docker](https://www.docker.com/)
2. Navigate to the project's root directory / the directory where docker-compose files are located
3. Run `docker-compose up`

### Tests

To run tests,

1. Initially, run: `DOMAIN=backend sh ./scripts/test-local.sh`
2. For subsequent tests, run `docker-compose exec backend /app/tests-start.sh`

You can pass pytest arguments at the end of the previous command. E.g. 

`DOMAIN=backend sh ./scripts/test-local.sh -k test_it_also_deletes_rows_in_room_players`

`docker-compose exec backend /app/tests-start.sh -k test_it_also_deletes_rows_in_room_players`


![tests](./_assets/tests.png)

## License
See LICENSE file in this repo. 😄
