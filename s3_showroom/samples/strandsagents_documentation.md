# Strands Agents

## Project Overview

Strands Agents is an AWS SDK for Python that provides a model-driven approach to building AI agents with just a few lines of code. It's designed as a lightweight, flexible framework that scales from simple conversational assistants to complex autonomous workflows, supporting both local development and production deployment.

**Key Features:**
- **Lightweight & Flexible**: Simple agent loop that's fully customizable
- **Model Agnostic**: Support for Amazon Bedrock, Anthropic, LiteLLM, Llama, Ollama, OpenAI, and custom providers
- **Advanced Capabilities**: Multi-agent systems, autonomous agents, and streaming support
- **Built-in MCP**: Native support for Model Context Protocol (MCP) servers with thousands of pre-built tools
- **Python-First**: Easy tool creation using Python decorators and type hints

The project is currently in **public preview** status, with APIs potentially changing as the SDK is refined based on community feedback.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- AWS credentials configured (for default Bedrock provider)
- Model access enabled for Claude 3.7 Sonnet in us-west-2 region (for default setup)

### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Strands and tools
pip install strands-agents strands-agents-tools
```

### Quick Start

The simplest way to get started is with a basic agent:

```python
from strands import Agent
from strands_tools import calculator

# Create an agent with a calculator tool
agent = Agent(tools=[calculator])

# Use the agent
result = agent("What is the square root of 1764?")
print(result)
```

### Custom Tools

Create your own tools using the `@tool` decorator:

```python
from strands import Agent, tool

@tool
def word_count(text: str) -> int:
    """Count words in text.
    
    This docstring is used by the LLM to understand the tool's purpose.
    """
    return len(text.split())

agent = Agent(tools=[word_count])
response = agent("How many words are in this sentence?")
```

### Model Configuration

Switch between different model providers:

```python
from strands import Agent
from strands.models import BedrockModel
from strands.models.ollama import OllamaModel
from strands.models.openai import OpenAIModel

# Bedrock (default)
bedrock_agent = Agent(model=BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.3,
    streaming=True
))

# Ollama
ollama_agent = Agent(model=OllamaModel(
    host="http://localhost:11434",
    model_id="llama3"
))

# OpenAI
openai_agent = Agent(model=OpenAIModel(
    model_id="gpt-4",
    api_key="your-api-key"
))
```

## Architecture

Strands Agents follows a clean, event-driven architecture designed around the core concept of an **Agent Loop**. The framework emphasizes modularity, extensibility, and simplicity while providing powerful capabilities for AI agent development.

### Project Structure

```
src/strands/
├── agent/                    # Core agent implementation
│   ├── agent.py             # Main Agent class
│   ├── agent_result.py      # Result handling
│   └── conversation_manager/ # Context management
├── event_loop/              # Agent execution loop
│   ├── event_loop.py        # Core event processing
│   ├── message_processor.py # Message handling
│   └── streaming.py         # Streaming support
├── models/                  # Model provider implementations
│   ├── bedrock.py          # AWS Bedrock
│   ├── anthropic.py        # Anthropic Claude
│   ├── openai.py           # OpenAI GPT
│   ├── ollama.py           # Ollama
│   └── litellm.py          # LiteLLM proxy
├── tools/                   # Tool system
│   ├── decorator.py         # @tool decorator
│   ├── registry.py          # Tool management
│   ├── executor.py          # Tool execution
│   └── mcp/                 # MCP integration
├── types/                   # Type definitions
│   ├── content.py          # Message/content types
│   ├── models/             # Model interfaces
│   └── tools.py            # Tool types
├── handlers/                # Event handling
├── telemetry/              # Observability
└── multiagent/             # Multi-agent systems
```

### Key Components

**Agent (`src/strands/agent/agent.py`)**
- Primary interface for users
- Orchestrates conversation flow
- Manages tools and model interactions
- Supports both natural language calls (`agent("prompt")`) and direct tool calls (`agent.tool.function_name()`)

**Event Loop (`src/strands/event_loop/event_loop.py`)**
- Core execution engine
- Handles model inference cycles
- Manages tool execution
- Implements retry logic and error recovery
- Supports parallel tool execution

**Tool System (`src/strands/tools/`)**
- Decorator-based tool creation
- Automatic schema generation from type hints
- MCP (Model Context Protocol) integration
- Hot-reloading during development
- Registry-based tool management

**Model Providers (`src/strands/models/`)**
- Pluggable model interface
- Support for multiple LLM providers
- Streaming and structured output support
- Provider-specific optimizations

### ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│  agent("prompt")           agent.tool.function_name()            │
│       │                              │                          │
│       └──────────────┬─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT CORE                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Agent Loop     │────│  Conversation   │────│  Tool       │  │  
│  │  Controller     │    │  Manager        │    │  Registry   │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EVENT LOOP                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Message        │────│  Tool           │────│  Streaming  │  │
│  │  Processor      │    │  Executor       │    │  Handler    │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATIONS                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Model          │    │  Tool System    │    │  Telemetry  │  │
│  │  Providers      │    │                 │    │  & Tracing  │  │
│  │                 │    │  ┌───────────┐  │    │             │  │
│  │ • Bedrock       │    │  │ @tool     │  │    │ • Metrics   │  │
│  │ • Anthropic     │    │  │ Functions │  │    │ • Traces    │  │
│  │ • OpenAI        │    │  └───────────┘  │    │ • Logging   │  │
│  │ • Ollama        │    │  ┌───────────┐  │    │             │  │
│  │ • LiteLLM       │    │  │ MCP       │  │    │             │  │
│  │ • Custom        │    │  │ Servers   │  │    │             │  │
│  └─────────────────┘    │  └───────────┘  │    └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core Dependencies:**
- `boto3` & `botocore`: AWS Bedrock integration
- `pydantic`: Data validation and schema generation
- `mcp`: Model Context Protocol support
- `docstring_parser`: Tool metadata extraction
- `opentelemetry`: Observability and tracing

**Optional Model Providers:**
- `anthropic`: Direct Anthropic API access
- `openai`: OpenAI API integration
- `ollama`: Local model serving
- `litellm`: Multi-provider proxy
- `mistralai`: Mistral AI models

### Data Flow and Execution Patterns

1. **User Input Processing**: User provides natural language prompt or direct tool call
2. **Message Management**: Conversation manager handles context and history
3. **Event Loop Execution**: Core loop processes messages through model inference
4. **Tool Execution**: If model requests tools, they're executed in parallel when possible
5. **Response Generation**: Final response is formatted and returned with metrics
6. **Context Management**: Conversation history is managed for subsequent interactions

### Design Patterns

**Decorator Pattern**: The `@tool` decorator transforms functions into agent-compatible tools
**Registry Pattern**: Tools are managed through a centralized registry system
**Strategy Pattern**: Different model providers implement a common interface
**Observer Pattern**: Callback handlers for event processing and monitoring
**Context Manager Pattern**: MCP clients use context managers for resource management

## Project Evolution

### Development Activity

**Recent Development (Last 2 months):**
- **115 total commits** since project inception (May 16, 2025)
- **141 tracked files** showing comprehensive feature set
- Active development with commits as recent as June 27, 2025
- Focus on model provider expansion and tooling improvements

**Recent Key Features Added:**
- Mistral model support integration
- Enhanced OpenAI reasoning content support
- Multi-agent systems (A2A - Agent-to-Agent)
- Iterative structured output capabilities
- Improved error handling and debugging
- Enhanced telemetry and tracing capabilities

### Branch Strategy

- **main**: Primary development branch
- **v0.1.x**: Maintenance branch for version 0.1 series
- Clean branching strategy indicating mature development practices

### Project Health Indicators

**Positive Indicators:**
- **Comprehensive test coverage**: Extensive unit tests and integration tests
- **Multiple model provider support**: Not locked to single vendor
- **Active feature development**: Regular commits with meaningful improvements
- **Professional documentation**: Well-structured README and inline documentation
- **Industry standard practices**: Proper packaging, linting, type hints

**Preview Status Considerations:**
- APIs may change as the SDK matures
- Community feedback actively sought
- Rapid iteration and improvement cycle
- Forward-looking architecture design

### Development Patterns

**Code Quality Focus:**
- Type hints throughout codebase (`mypy` compliance)
- Comprehensive testing (unit + integration)
- Code formatting and linting (`ruff`)
- Pre-commit hooks for quality assurance

**Architecture Evolution:**
- Started with simple agent concept
- Expanded to multi-agent systems
- Added streaming capabilities
- Integrated observability features
- Built comprehensive tool ecosystem

The project demonstrates strong engineering practices and architectural vision, positioning it well for production use despite its preview status. The active development and comprehensive feature set suggest a mature approach to AI agent development frameworks.