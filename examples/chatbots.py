# origin https://python.langchain.com/docs/use_cases/chatbots/quickstart/#handling-documents
import os

from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from prompt_wave import PromptWave

# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

chat_history = ChatMessageHistory()
wave = PromptWave()
Input, Depend = wave.hooks

chain = wave([
    (
        "system", "You are a helpful assistant. Answer all questions to the best of your ability.",
    ),
    Depend(lambda _: chat_history.messages, message_placeholder=True),
]) | ChatOpenAI(temperature=0.2) | StrOutputParser()

if __name__ == '__main__':
    wave.prompt.pretty_print()
    print('\n########OUTPUT#########')
    while 1:
        chat_history.add_user_message(input('You:'))
        response = chain.invoke({})
        print(f'AI:{response}')
        chat_history.add_ai_message(response)
