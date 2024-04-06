import os
from operator import itemgetter

# pip install wikipedia
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI

from prompt_wave import PromptWave

# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'


wiki = WikipediaAPIWrapper(top_k_results=5)
wave = PromptWave()
Input, Depend = wave.hooks


@chain
def Search(query):
    res = wiki.run(query)
    return res


chain = wave(f"""Answer the users question based only on the following context:

<context>
{Depend(itemgetter('question') | Search)}
</context>
 
Question: {Input('question')}""") | ChatOpenAI(temperature=0) | StrOutputParser()

if __name__ == '__main__':
    wave.prompt.pretty_print()
    print('\n########OUTPUT#########')
    print(chain.invoke({'question': "what is langchain?"}))
