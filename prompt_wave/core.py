import logging
import uuid
from operator import itemgetter
from typing import Optional, Union, Sequence, Dict, Any, List

from langchain.chains.base import Chain
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.messages import MessageLikeRepresentation
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig, RunnableAssign, RunnablePassthrough
from langchain_core.runnables.utils import Input, Output

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

    def Depend(self, runnable: RunnableLike, key: str = Auto):
        if key == Auto:
            key = f"Runnable Input:{uuid.uuid1()}"
        self.container.set(key, runnable)
        return '{' + key + '}'

    def Input(self, key):
        self.container.set(key, itemgetter(key))
        return '{' + key + '}'

    @property
    def hooks(self):
        return self.Input, self.Depend

    def __call__(self, temple: Union[Sequence[MessageLikeRepresentation]]):
        if isinstance(temple, str):
            temple = [('human', temple)]
        prompt = ChatPromptTemplate.from_messages(temple)
        runnable_dict = {}
        for k in prompt.input_variables:
            runnable = self.get_runnable(k)
            if not isinstance(runnable, itemgetter):
                runnable_dict[k] = runnable
        return (
                RunnablePassthrough.assign(**runnable_dict) | prompt
        )

    def get_runnable(self, key):
        v = self.container.get(key)
        if not v:
            logger.error(f'can not find key:{key}')
        return v
