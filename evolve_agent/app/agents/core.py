import json
from typing import Any, Dict

from .models import get_model
from .rag import TemplateRAG


class Agent:
    def __init__(self):
        rag_model, rag_embeddings = get_model(model_id="ollama/llama3.2", format="json")
        self.rag = TemplateRAG(model=rag_model, embeddings=rag_embeddings)

    def get_workflow(self, query: str) -> Dict[str, Any]:
        response = self.rag.query(query)
        return json.loads(response["answer"])


if __name__ == "__main__":
    agent = Agent()
    response = agent.get_workflow(
        "How can I set up a WhatsApp chatbot that can send me weather of Singapore each hour?"
    )
    print(response)
