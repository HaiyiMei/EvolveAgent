from langchain import hub

# prompt = hub.pull("rlm/rag-prompt")
rag_prompt = """
You are an expert at understanding and explaining workflow templates.
And you are given the following template information:
{context}

Answer the question based on the templates provided:

Question: {input}

Remember to:
1. Imitate the style of the template
2. Make sure to return in a WELL-FORMED JSON object
3. Focus on the "nodes" and "connections" keys
"""
