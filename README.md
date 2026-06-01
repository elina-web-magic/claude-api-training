# Building with the Claude API - Training Course

This repository contains code examples, exercises, and projects developed as part of the **Building with the Claude API** training course by Anthropic.

The goal of this course is to master integrating Anthropic's Claude models into applications, utilizing advanced prompting, tool use, Retrieval-Augmented Generation (RAG), and agentic workflows.

---

## Course Syllabus & Overview

### 1. Introduction

* **Welcome to the course**: Getting started with API integrations and setting expectations.
* **Anthropic overview**: Understanding Anthropic's mission and the landscape of Claude models.

### 2. Accessing Claude with the API

* **Accessing the API**: Setting up the environment, dependencies, and clients.
* **Getting an API key**: Securing and managing Anthropic API credentials.
* **Making a request**: Structure of basic API calls.
* **Multi-Turn conversations**: Maintaining conversation history and state.
* **Chat exercise**: Interactive chat application implementation.
* **System prompts & exercise**: Configuring behavior using system prompts.
* **Temperature**: Adjusting deterministic vs. creative output generation.
* **Response streaming**: Handling real-time token streaming for active UI.
* **Structured data & exercise**: Enforcing and parsing JSON/structured responses from Claude.
* **Assessment**: Course satisfaction survey & Accessing Claude quiz.

### 3. Prompt Evaluation

* **A typical eval workflow**: Establishing reliable, repeatable evaluation pipelines.
* **Generating test datasets**: Creating synthetic and real evaluation data.
* **Running the eval**: Orchestrating run configurations on datasets.
* **Grading models**: Comparison of Model-based grading (LLM-as-a-judge) vs. Code-based grading (assertions, exact matches).
* **Exercise on prompt evals & quiz**: Hands-on evaluation implementation.

### 4. Prompt Engineering Techniques

* **Core principles**: Being clear, direct, and specific.
* **Structure with XML tags**: Utilizing canonical XML markers (`<tag></tag>`) to isolate inputs, instructions, and context.
* **Providing examples**: Implementing few-shot prompting techniques.
* **Exercise & quiz**: Practical engineering optimization challenges.

### 5. Tool Use (Function Calling) with Claude

* **Introducing tool use**: Allowing Claude to interact with external tools and APIs.
* **Project overview & tool functions**: Writing python functions to act as tools.
* **Tool schemas**: Specifying JSON schemas to declare function arguments and descriptions.
* **Handling message blocks**: Parsing tool use calls and constructing tool result responses.
* **Multi-turn conversations with tools**: Managing full loops where Claude repeatedly calls tools to solve a problem.
* **Specialized tools**:
  * **The text edit tool**: Fine-grained code/text modifications.
  * **The web search tool**: Fetching live web search results.
* **Assessment**: Practical tool-use exercises and quiz.

### 6. RAG and Agentic Search

* **Introducing Retrieval-Augmented Generation**: Supplementing prompts with external documents.
* **Text chunking strategies**: Dividing long texts intelligently to preserve context.
* **Text embeddings**: Vectorizing text chunks for semantic searches.
* **RAG implementation**: Putting together the vector database query and retrieval loop.
* **Advanced search pipelines**:
  * **BM25 lexical search**: Classic keyword-based search.
  * **Multi-Index RAG pipeline**: Combining multiple indexes for comprehensive retrieval.

### 7. Features of Claude

* **Extended thinking**: Leveraging long-form thinking blocks for complex reasoning.
* **Image & PDF support**: Multi-modal prompting with document files and images.
* **Citations**: Requesting precise source references from Claude.
* **Prompt caching**: Speeding up response times and lowering costs by caching reusable prompt contexts.
* **Code execution**: Utilizing the Files API to run code dynamically in a secure environment.

### 8. Model Context Protocol (MCP)

* **Introducing MCP**: The open standard for connecting AI assistants to data sources and tools.
* **MCP clients & servers**: Architecture, inspector tools, and client-server communication.
* **Project setup & implementation**:
  * Defining tools, resources, and prompts with MCP.
  * Accessing dynamic prompts in the client.

### 9. Anthropic Apps: Claude Code & Computer Use

* **Claude Code setup & action**: Working with Anthropic's interactive command-line tool.
* **Enhancements with MCP servers**: Connecting Claude Code to custom integrations.
* **Computer use**: Allowing agents to interact with a computer interface directly (UI/clicks).

### 10. Agents and Workflows

* **Workflows vs. Agents**: Choosing between structured pipelines and autonomous agents.
* **Common Workflows**:
  * **Parallelization**: Fan-out and fan-in workflows.
  * **Chaining**: Step-by-step pipeline execution.
  * **Routing**: Directing traffic to specialized prompts or sub-agents.
  * **Environment inspection**: Iteratively checking agent states.

### 11. Final Assessment & Wrap Up

* **Final Assessment**: Testing complete comprehension of course materials.
* **Course Wrap Up**: Summary of accomplishments and best practices for production deployments.

---

## Getting Started

### 1. Prerequisites

* Python 3.10+

* Anthropic API Key

### 2. Installation

Clone the repository, create a virtual environment, and install dependencies:

```bash
git clone https://github.com/elina-web-magic/claude-api-training.git
cd claude-api-training
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Copy the `.env.example` to `.env` and fill in your Anthropic API Key:

```bash
cp .env.example .env
```

Open `.env` and configure your key:

```env
ANTHROPIC_API_KEY=your_api_key_here
```
