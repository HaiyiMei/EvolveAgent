![EvolveAgent](./assets/cover.jpeg)

<h2>
    <p align="center">
    🤖 EvolveAgent
    </p>
</h2>

## Overview

![clip.mp4](./assets/clip.mp4)

The EvolveAgent system implements a pipeline for automated workflow generation, execution, and iterative improvement.

The main pipeline is defined in [evolve_agent/agents/core.py@pipeline](evolve_agent/agents/core.py#L192) and orchestrates the interaction between multiple agent components:

### Playground

- N8N as the workflow engine.

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

The pipeline implements an iterative improvement process with automatic error handling and retries:
- Maintains detailed logging of each attempt
- Archives previous workflow versions
- Handles workflow execution errors gracefully
- Supports multiple retry attempts with refined prompts

### Technology Stack

- [N8N](https://n8n.io/) as the workflow engine. [~~(Dify)~~](https://dify.ai/)
- [LangChain](https://www.langchain.com/) as the framework for the agents and RAG
- [FastAPI](https://fastapi.tiangolo.com/) as the API server

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

## BUGs:

- In docker-compose production
  - n8n service has issue with create a new workflow and save it.
  - the webhook cannot be accessed from backend(evolve_agent) yet.
  - the ollama embeddings cannot be accessed.
- N8N_PUBLIC_URL is not working.
