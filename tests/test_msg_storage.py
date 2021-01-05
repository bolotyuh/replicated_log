from shared.msg_storage import MsgList
from shared.models import Message


def test_append_message():
    storage = MsgList()
    assert storage.get_all() == []
    storage.append(Message(message="test"))
    assert storage.count() == 1


def test_count():
    storage = MsgList()
    assert storage.count() == 0
    storage.append(Message(message="test"))
    storage.append(Message(message="test"))
    storage.append(Message(message="test"))
    assert storage.count() == 3
