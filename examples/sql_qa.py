import os
from operator import itemgetter

from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from prompt_wave import PromptWave

# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# setup
wave = PromptWave()
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
Input, Depend = wave.hooks


chain = wave(
    f"""Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {Input('question')}
SQL Query: {Depend(create_sql_query_chain(llm, db), key='query', level=-1, description='run before SQL Result')}
SQL Result: {Depend(itemgetter("query") | QuerySQLDataBaseTool(db=db))}
Answer: """
) | llm | StrOutputParser()

if __name__ == '__main__':
    print(chain.invoke({"question": "How many employees are there"}))