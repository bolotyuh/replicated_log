from typing import List
import logging

from shared.models import Message

logger = logging.getLogger(__name__)


class MsgList:
    def __init__(self) -> None:
        self.__data: List[Message] = []

    def __new__(cls) -> "MsgList":
        if not hasattr(cls, 'instance'):
            cls.instance = super(MsgList, cls).__new__(cls)
        return cls.instance

    def get_ordered_json(self) -> List:
        if self.count() > 0:
            return [msg.dict() for msg in self.get_ordered()]
        else:
            return []

    def get_ordered(self):
        if len(self.__data) <= 0:
            return self.__data

        order_index = {m.order: m for m in self.__data}
        max_order = max(order_index.keys())

        template = set(range(max_order))
        diff = template.difference(set(order_index.keys()))

        result = []
        for i in range(max_order + 1):
            if i in diff:
                result.append(None)
            else:
                result.append(order_index[i])

        if None in result:
            return result[0:result.index(None)]
        else:
            return result

    def get_all(self) -> List[Message]:
        return self.__data

    def append(self, msg: Message) -> None:
        if msg not in self.__data:
            self.__data.append(msg)
        else:
            logger.info(f'Message already exist on master node: "{msg}"')

    def count(self) -> int:
        return len(self.__data)
