from langchain_openai import ChatOpenAI
from trip_weaver.config.settings import OPENAI_API_KEY,MODEL_NAME

model_client = ChatOpenAI(
    model=MODEL_NAME, 
    api_key=OPENAI_API_KEY,
    stream_usage=True)