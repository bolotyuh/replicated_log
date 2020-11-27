from pydantic import BaseModel


class Message(BaseModel):
    message: str


class AppendMessage(Message):
    w: int  # specifies how many ACKs the master should receive
