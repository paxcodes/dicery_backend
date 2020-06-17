import string
import secrets

def GenerateRoomCode() -> str:
    """Generates an alphanumeric 5-digit room code"""
    alphabet = string.ascii_uppercase + string.digits
    roomCode = ''.join(secrets.choice(alphabet) for i in range(5))
    # TODO make sure that roomCode is unique/does not exist yet.
    return roomCode