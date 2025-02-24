import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()


def get_anthropic_model(model_id: str = "claude-3.5-sonnet"):
    return ChatOpenAI(model_name=model_id, openai_api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_openai_model(model_id: str = "gpt-4o"):
    return ChatOpenAI(model_name=model_id, openai_api_key=os.getenv("OPENAI_API_KEY"))


def get_ollama_model(model_id: str = "llama3.2"):
    return ChatOllama(model=model_id, base_url="http://localhost:11434")


if __name__ == "__main__":
    model = get_ollama_model()
    response = model.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is the capital of France?"),
        ]
    )
    print(response.content)
