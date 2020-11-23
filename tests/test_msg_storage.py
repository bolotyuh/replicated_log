from master.app.msg_storage import MsgStorage
from master.app.models import Message


def test_append_message():
    storage = MsgStorage()
    assert storage.get_all() == []
    storage.append(Message(message="test"))
    assert storage.count() == 1


def test_count():
    storage = MsgStorage()
    assert storage.count() == 0
    storage.append(Message(message="test"))
    storage.append(Message(message="test"))
    storage.append(Message(message="test"))
    assert storage.count() == 3
