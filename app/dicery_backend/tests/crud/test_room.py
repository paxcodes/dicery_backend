from dicery_backend import crud, schemas
from pytest import fixture, mark
from sqlalchemy.orm import Session


class Test_Room_BREAD:
    @fixture(scope="class")
    def givenRoom(self, db: Session):
        givenRoomCode, givenOwner = "ABCDE3", "Pax"
        roomSchema = schemas.RoomCreate(code=givenRoomCode, owner=givenOwner)
        # TODO creating a room should automatically create a room player
        room = crud.create_room(db, roomSchema=roomSchema)
        roomPlayer = schemas.RoomPlayer(room_code=givenRoomCode, player=givenOwner)
        crud.add_room_player(db, roomPlayer)
        yield room
        crud.delete_room(db, room_code=givenRoomCode)

    def test_it_can_close_the_room(self, db: Session, givenRoom):
        # When
        crud.close_room(db, givenRoom.code)
        db.refresh(givenRoom)
        # Then
        assert not givenRoom.isAvailable

    class Test_When_the_only_room_is_deleted:
        @fixture(scope="class")
        def givenRoom(self, db: Session):
            givenRoomCode, givenOwner = "ABCDE4", "Pax"
            roomSchema = schemas.RoomCreate(code=givenRoomCode, owner=givenOwner)
            # TODO creating a room should automatically create a room player
            room = crud.create_room(db, roomSchema=roomSchema)
            roomPlayer = schemas.RoomPlayer(room_code=givenRoomCode, player=givenOwner)
            crud.add_room_player(db, roomPlayer)
            crud.delete_room(db, room_code=room.code)
            yield room

        def test_it_also_deletes_rows_in_room_players(self, db: Session, givenRoom):
            actualPlayers = crud.get_room_players(db, givenRoom.code)
            assert actualPlayers == []

        def test_there_should_be_no_more_players_in_the_database(self, db: Session):
            actualAllPlayers = crud.get_all_players(db)
            assert actualAllPlayers == []

    class Test_When_a_room_is_deleted_and_other_rooms_exist:
        @mark.skip(reason="Test not yet created")
        def test_it_deletes_room_players_of_the_deleted_room(self, db: Session):
            # TODO
            pass

        @mark.skip(reason="Test not yet created")
        def test_players_in_the_other_room_should_still_be_present(self, db: Session):
            # TODO
            pass
