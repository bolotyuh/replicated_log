from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    id: Optional[int]
    message: str
    order: Optional[int]

    def __key(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.__key() == other.__key()
        return NotImplemented

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.id < other.id


class AppendMessage(BaseModel):
    message: str
    w: int  # specifies how many ACKs the master should receive
