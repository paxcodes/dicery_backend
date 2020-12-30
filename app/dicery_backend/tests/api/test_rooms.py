from typing import Generator

from pytest import fixture, mark
from sqlalchemy.orm import Session

from dicery_backend import crud, schemas, models
from starlette.testclient import TestClient


class Test_when_room_is_unavailable:
    """Tests that when room is marked as closed / "isAvailable" == False,
    user will not be able to get an access token for it."""

    @fixture
    def givenClosedRoom(self, db: Session) -> Generator[models.Room, None, None]:
        roomSchema = schemas.RoomCreate(code="ABCDE1", owner="Pax")
        room = crud.create_room(db, roomSchema)
        crud.close_room(db, room_code=room.code)
        yield room
        crud.delete_room(db, room_code=room.code)

    def test_players_cannot_receive_access_token_for_room(
        self, client: TestClient, givenClosedRoom: models.Room
    ):
        response = client.post(
            "/token", data={"room_code": givenClosedRoom.code, "player": "Sean"}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Room not found"}


class Test_when_unauthorized_player_attempts_to_enter_room:
    @mark.skip(reason="Test not yet implemented")
    def test_api_responds_with_403_FORBIDDEN(self):
        pass
