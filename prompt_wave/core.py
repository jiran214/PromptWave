import logging
import uuid
from operator import itemgetter
from typing import Optional, Union, Sequence

from langchain_core.messages import MessageLikeRepresentation
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

from langchain_core.runnables.base import RunnableLike

logger = logging.getLogger(__name__)

Auto = '__auto__'


class Container:
    obj_pool = {}

    def set(self, key, obj):
        if key in self.obj_pool:
            logger.warning(f'key:{key} already exists')
        self.obj_pool[key] = obj

    def get(self, key):
        return self.obj_pool.get(key)

    def delete(self, key):
        return self.obj_pool.pop(key)


class PromptWave:
    def __init__(self):
        self.container = Container()
        self.priority_map = {}
        self.prompt: Optional[ChatPromptTemplate] = None

    def Depend(
            self,
            runnable: RunnableLike,
            key: str = Auto,
            level: int = 0,
            message_placeholder=False,
            description=''
    ):
        if key == Auto:
            key = f"RunnableInput_{uuid.uuid1()}"
        if level not in self.priority_map:
            self.priority_map[level] = []
        self.priority_map[level].append(key)
        self.container.set(key, runnable)
        if message_placeholder:
            return MessagesPlaceholder(variable_name=key)
        return '{' + key + '}'

    def Input(self, key):
        return '{' + key + '}'

    @property
    def hooks(self):
        return self.Input, self.Depend

    def __call__(self, temple: Union[Sequence[MessageLikeRepresentation]]):
        if isinstance(temple, str):
            temple = [('human', temple)]
        self.prompt = ChatPromptTemplate.from_messages(temple)
        sorted_level_keys = sorted(self.priority_map.keys())
        chain = RunnablePassthrough()
        for level in sorted_level_keys:
            runnable_dict = {}
            input_keys = self.priority_map[level]
            for k in input_keys:
                runnable = self.get_runnable(k)
                runnable_dict[k] = runnable
            if runnable_dict:
                chain = chain.assign(**runnable_dict)
        chain |= self.prompt
        return chain

    def get_runnable(self, key):
        v = self.container.get(key)
        return v
