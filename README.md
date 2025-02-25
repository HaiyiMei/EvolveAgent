![EvolveAgent](./assets/cover.jpeg)

<h2>
    <p align="center">
    🤖 EvolveAgent: Self-evolving workflow automation
    </p>
</h2>

## Overview

https://github.com/user-attachments/assets/d3ac5ea7-164e-4d3a-9034-4005ae2cd9d8

The EvolveAgent system implements a pipeline for automated workflow generation, execution, and iterative improvement.

Below are the key components and configurations:

- [pipeline](evolve_agent/agents/core.py#L193): The main pipeline that orchestrates the entire workflow generation, execution, and iterative improvement.
- [prompt](evolve_agent/agents/prompt.py): The prompt for the meta-agent and rag-agent.

### Playground

- **N8N**: The workflow automation engine that provides:
  - Workflow file structure and templates
  - Execution environment
  - Webhook triggers for workflow execution

### Pipeline Process

1. **Meta-Agent**
    - Provides guidelines for the RAG-Agent
    - Analyzes previous workflow attempts
    - Reflects on errors and suggests improvements
    - Helps optimize the workflow generation process

2. **RAG-Agent**
    - Generates new workflow templates based on Meta-Agent guidelines
    - Incorporates feedback from previous attempts
    - Adapts to error cases and refines solutions

### Iterative Improvement Process

The pipeline implements automatic error handling and continuous improvement through:
- Detailed logging of each attempt
- Version control of workflow iterations
- Graceful error handling
- Multiple retry attempts with refined prompts

### Technology Stack

- [N8N](https://n8n.io/) - Workflow automation engine
- [LangChain](https://www.langchain.com/) - Framework for agents and RAG
- [FastAPI](https://fastapi.tiangolo.com/) - API server

## Setup

```bash
docker compose down; docker compose up -d --build
```

## Dataset For RAG

- n8n-workflow-template

https://github.com/Stirito/N8N_Workflow_Template

https://waha-n8n-templates.devlike.pro/

https://n8n.io/workflows/

https://www.firecrawl.dev/app

## TODO:

- [ ] Collect more templates and do a better RAG agent.

- [ ] Add synthetic data as input/output of the generated workflow, to test the correctness and efficiency of the evolved workflow.

## BUGs:

- In docker-compose production
  - n8n service has issue with create a new workflow and save it.
  - the webhook cannot be accessed from backend(evolve_agent) yet.
  - the ollama embeddings cannot be accessed.
- N8N_PUBLIC_URL is not working.

## References

- [ADAS](https://github.com/ShengranHu/ADAS)
- [AdaFlow](https://github.com/SylphAI-Inc/AdalFlow)
- [Symbolic Learning](https://github.com/aiwaves-cn/agents)
