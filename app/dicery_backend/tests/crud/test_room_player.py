from dicery_backend import crud
from dicery_backend.schemas import RoomCreate, RoomPlayer
from pytest import fixture
from sqlalchemy.orm import Session


class Test_RoomPlayer_CRUD:
    @fixture
    def givenRoom(self, db: Session):
        # TODO creating a room SHOULD automatically add owner in room_player
        room_code, player = "ABCDEF", "Pax"
        room = RoomCreate(code=room_code, owner=player)
        crud.create_room(db, roomSchema=room)
        room_player = RoomPlayer(room_code=room.code, player=player)
        crud.add_room_player(db, room_player=room_player)
        yield room
        crud.delete_room(db, room.code)

    def test_owner_is_included_in_lists_of_players_in_a_room(
        self, db: Session, givenRoom
    ) -> None:
        actualPlayers = crud.get_room_players(db, room_code=givenRoom.code)
        assert actualPlayers == [givenRoom.owner]
