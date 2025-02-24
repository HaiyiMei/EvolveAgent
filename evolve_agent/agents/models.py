import os
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .constants import model_ids

load_dotenv()


def get_openai_model(
    model_id: str = "gpt-4o",
    format: Literal["json", "text"] = "json",
    temperature: Optional[float] = None,
):
    if format == "json":
        model_kwargs = {"response_format": {"type": "json_object"}}
    else:
        model_kwargs = {}

    model = ChatOpenAI(
        model_name=model_id,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_kwargs=model_kwargs,
        temperature=temperature,
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    return model, embeddings


def get_ollama_model(
    model_id: str = "llama3.2",
    format: Literal["json", "text"] = "json",
    temperature: Optional[float] = None,
):
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"Using Ollama base URL: {ollama_base_url}")
    model = ChatOllama(
        model=model_id,
        base_url=ollama_base_url,
        format=format,
        temperature=temperature,
    )
    embeddings = OllamaEmbeddings(model=model_id)
    return model, embeddings


def get_model(
    model_id: model_ids = "ollama/llama3.2",
    format: Literal["json", "text"] = "json",
    temperature: Optional[float] = None,
):
    if "ollama" in model_id:
        return get_ollama_model(model_id.split("/")[1], format, temperature)
    elif "openai" in model_id:
        return get_openai_model(model_id.split("/")[1], format, temperature)


if __name__ == "__main__":
    model, embeddings = get_ollama_model()
    embeddings.embed_query("What is the capital of France?")
    response = model.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is the capital of France?"),
        ]
    )
    print(response.content)
