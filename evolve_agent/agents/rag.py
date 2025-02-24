import json
from pathlib import Path
from typing import Dict, List

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from loguru import logger

from .prompt import get_rag_prompt

root = Path(__file__).parent
project_root = root.parent
templates_dir = project_root / "templates" / "dataset"


class JSONTemplateLoader:
    def __init__(self, directory_path: Path):
        self.directory_path = directory_path

    def load(self) -> List[Document]:
        documents = []
        for filename in self.directory_path.iterdir():
            if filename.suffix == ".json":
                with open(filename, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    # Convert JSON to string while preserving structure
                    text = json.dumps(content, indent=2)
                    metadata = {
                        "source": str(filename.name),  # Convert to string
                        "type": "template",
                        "path": str(filename),  # Store full path as string
                    }
                    documents.append(Document(page_content=text, metadata=metadata))
        return documents


class TemplateRAG:
    """RAG system for querying and understanding workflow templates."""

    def __init__(
        self,
        model: ChatOllama | ChatOpenAI,
        embeddings: OllamaEmbeddings | OpenAIEmbeddings,
        templates_dir: Path = templates_dir,
    ):
        """Initialize the RAG system.

        Args:
            templates_dir: Directory containing JSON template files
            model: Language model to use for generation
            embeddings: Embeddings model to use for vector store
        """
        self.templates_dir = templates_dir
        self.model = model
        self.embeddings = embeddings

        self.loader = JSONTemplateLoader(templates_dir)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        self.vectorstore = None
        self.retrieval_chain = None
        self.initialize()

    def initialize(self):
        """Initialize the RAG system by loading documents and setting up the retrieval
        chain."""
        if (self.templates_dir / "chroma.sqlite3").exists():
            logger.info("[RAG] Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=str(self.templates_dir),
                embedding_function=self.embeddings,
                collection_name="workflow_templates",
            )
        else:
            logger.info("[RAG] Creating new vector store...")
            documents = self.loader.load()
            split_documents = self.text_splitter.split_documents(documents)

            self.vectorstore = Chroma.from_documents(
                documents=split_documents,
                embedding=self.embeddings,
                persist_directory=str(self.templates_dir),
            )

        rag_prompt = get_rag_prompt()

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        document_chain = create_stuff_documents_chain(self.model, rag_prompt)
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        logger.info("[RAG] System initialized")

    def query(
        self,
        question: str,
        archive: str = None,
        errors: str = None,
        guidelines: str = None,
    ) -> Dict:
        """Query the RAG system about workflow templates.

        Args:
            question: The question or query about workflow templates
            archive: The archive of the discovered architectures
            errors: The errors that happened in the last archive workflow
            guidelines: The guidelines for the RAG system

        Returns:
            Dict containing the answer and other relevant information
        """
        if not self.retrieval_chain:
            raise ValueError("RAG system not initialized. Call initialize() first.")
        return self.retrieval_chain.invoke(
            {"input": question, "archive": archive, "errors": errors, "guidelines": guidelines}
        )

    def get_relevant_templates(self, query: str, k: int = 3) -> List[Document]:
        """Get the most relevant templates for a query without generating an answer.

        Args:
            query: The search query
            k: Number of templates to retrieve

        Returns:
            List of relevant template documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call initialize() first.")
        return self.vectorstore.similarity_search(query, k=k)


if __name__ == "__main__":
    from .core import get_model

    print("Testing with Ollama model...")
    rag_model, rag_embeddings = get_model(model_id="ollama/llama3.2", format="json", temperature=0.2)
    rag = TemplateRAG(templates_dir=templates_dir, model=rag_model, embeddings=rag_embeddings)

    # 1. Test basic template querying
    print("\n=== Testing Simple Query ===")
    question = "How can I set up a WhatsApp chatbot using these templates?"
    print(f"\nQuestion: {question}")

    answer = rag.query(question)
    print("\nAnswer:")
    print(answer)

    # 2. Test template retrieval
    print("\n=== Testing Template Retrieval ===")
    query = "data analysis and visualization"
    print(f"\nQuery: {query}")

    templates = rag.get_relevant_templates(query, k=2)
    print(f"\nFound {len(templates)} relevant templates:")

    for i, doc in enumerate(templates, 1):
        print(f"\n{i}. Template: {doc.metadata['source']}")
        # Print first 200 characters of content as preview
        preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        print(f"Preview: {preview}")
        print(f"Preview: {preview}")
