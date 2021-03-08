# Backend API of Dicery

Dicery is a dice-rolling app where a group of friends can roll the dice and have their dice results broadcasted to everyone else. Basically, the API receives requests to:

- create a room
- add members to a room
- close a room
- broadcast dice results to users subscribed in a room using Server-Sent Events

## Running the API locally

1. Install Docker
2. Run `docker-compose up`

# Backend API of Dicery

## Personal Anecdotes

### Real-time event broadcasting

When researching on implementing real-time apps, I learned about Server-Sent Events (SSE) and how it’s a simpler mechanism than web sockets, yet sufficient to provide real-time event broadcasting for my app. Before I implemented SSE in the backend API, I implemented the simplest SSE endpoint that streams numbers. I researched for SSE in Python and found SSE-Starlette—a python package implementing the SSE protocol. I was able to use it, [fixed a bug](https://github.com/sysid/sse-starlette/pull/3) for them, and [helped other FastAPI users](https://github.com/sysid/sse-starlette/issues/2) use the package. This solidified my understanding before finally implementing it in the backend API.

### Securing Rooms
I had is securing rooms so no one outside the group can spam the room with dice rolls.

I read FastAPI's documentation on authorization where they mentioned OpenAPI's security schemes: API Keys, standard HTTP authentication, and oAuth2. The documentation focused on authorizing given a username and password, which is not relevant to my app that uses a room code.

The room code consists of 6 alphanumeric characters which can be cracked in under an hour and a table-top role-playing game can easily go for 2-4 hours. I know I shouldn't allow anyone with a valid room code to send POST requests to the API to submit dice rolls.

From the 3 security schemes, an API key of some sort (or something that works similarly) seems to be my best bet. Since the documentation didn’t talk about API keys, I had to dig into FastAPI’s repository to find out how FastAPI supports API keys. After studying how oAuth2 is implemented as written in the documentation and going through FastAPI’s security modules, I was able to come up with an equivalent for my app:

1. A user (the owner) creates a room and is given the room code.
 - The API receives a POST request which adds the room and the player to the database. A signed JWT containing the username and room code is created. The response will send back an HTTP-Only cookie containing the signed JWT.
2. The owner is moved to the lobby where players are listed as they join the room. There is also a button the owner clicks once everyone has joined.
 - The API receives a GET request which verifies the validity of the JWT. If the token is valid, the API sends an EventSourceResponse which broadcasts names of players joining the room’s lobby.
3. The owner informs their friend of the room code.
4. The friend submits the room code.
 - The API receives a POST request which adds a player to the database if the room code exists and is open to new members. A JWT containing the username and room code is created. The response will send back an HTTP-Only cookie containing the signed JWT.
5. Friends are transferred to the room’s lobby.
 - API has similar behaviour in Step 2.
6. Once everyone has joined, the owner clicks a button to close the room.
 - API receives a PUT request which flags the room as closed in the database. Once a room is closed, no new members can be added to the room.
7. All members are transported to the room where the results will be broadcasted to everyone in the room.
 - For every member of the room, the API receives a GET request which verifies the validity of the JWT. If the token is valid, the API sends an EventSourceResponse which broadcasts dice results to everyone subscribed to the room.
8. A user rolls a (or multiple) dice.
 - API receives a POST request which verifies the validity of the JWT. If the token is valid, the result is broadcasted to everyone else.

The token expires after 1 day. I’ve read that JWT is best used short-term (as short as 5 minutes, I read once) so perhaps it’s not an ideal solution. I also currently check whether the room code and player exist in the database and I wonder if it’s redundant since the JWT is already signed. I would have to review best practices when using JWTs.

### In the Wild

Although the solution may not be ideal, my husband and his friends were able to use it for a couple of game sessions until it was no longer necessary since they moved from Google Hangouts to Discord where they can install a dice-rolling bot. Check it out at https://stag.dicery.margret.pw/

