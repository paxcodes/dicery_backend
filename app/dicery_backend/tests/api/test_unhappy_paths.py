from typing import Generator

from dicery_backend import crud, models, schemas
from pytest import fixture, mark
from sqlalchemy.orm import Session
from starlette.testclient import TestClient


class Test_when_room_is_unavailable:
    """When room is marked as closed / "isAvailable" == False"""

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
        """User should not be able to get an access token for it."""
        response = client.post(
            "/token", data={"room_code": givenClosedRoom.code, "player": "Sean"}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Room not found"}


class Test_when_unauthorized_player_attempts_to_enter_room:
    @mark.skip(reason="Test not yet implemented")
    def test_api_responds_with_403_FORBIDDEN(self):
        pass
