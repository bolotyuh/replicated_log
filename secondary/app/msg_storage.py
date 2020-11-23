from typing import List

from .models import Message


class MsgStorage:
    def __init__(self) -> None:
        self.__data: List[Message] = []

    def __new__(cls) -> "MsgStorage":
        if not hasattr(cls, 'instance'):
            cls.instance = super(MsgStorage, cls).__new__(cls)
        return cls.instance

    def get_all(self) -> List[Message]:
        return self.__data

    def append(self, msg: Message) -> None:
        self.__data.append(msg)

    def count(self) -> int:
        return len(self.__data)
