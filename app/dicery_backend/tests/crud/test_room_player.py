from sqlalchemy.orm import Session

from dicery_backend.schemas import RoomCreate, RoomPlayer
from dicery_backend import crud


class Test_RoomPlayer_CRUD:
    def test_it_lists_players_in_a_room(self, db: Session) -> None:
        # Given
        room_code, player = "ABCDEF", "Pax"
        room = RoomCreate(code=room_code, owner=player)
        crud.create_room(db, room=room)
        room_player = RoomPlayer(room_code=room.code, player=player)
        crud.add_room_player(db, room_player=room_player)
        # When
        actualPlayers = crud.get_room_players(db, room_code=room.code)
        # Then
        assert actualPlayers == [player]
