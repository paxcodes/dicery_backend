from sqlalchemy.orm import Session

from dicery_backend import crud, schemas

from pytest import fixture


class Test_Room_BREAD:
    @fixture(scope="module")
    def givenRoom(self, db: Session):
        givenRoomCode = "ABCDE3"
        roomSchema = schemas.RoomCreate(code=givenRoomCode, owner="Pax")
        yield crud.create_room(db, roomSchema=roomSchema)
        crud.delete_room(db, room_code=givenRoomCode)

    def test_it_can_close_the_room(self, db: Session, givenRoom):
        # When
        crud.close_room(db, givenRoom.code)
        db.refresh(givenRoom)
        # Then
        assert not givenRoom.isAvailable
