import json
from typing import Any, Dict

from .models import get_model
from .rag import TemplateRAG


class Agent:
    def __init__(self):
        rag_model, rag_embeddings = get_model(
            model_id="openai/gpt-4o-mini",
            format="json",
            temperature=0,
        )
        self.rag = TemplateRAG(model=rag_model, embeddings=rag_embeddings)

    def generate_workflow(self, prompt: str) -> Dict[str, Any]:
        response = self.rag.query(prompt)
        return json.loads(response["answer"])


if __name__ == "__main__":
    agent = Agent()
    response = agent.generate_workflow(
        "How can I set up a WhatsApp chatbot that can send me weather of Singapore each hour?"
    )
    print(response)
