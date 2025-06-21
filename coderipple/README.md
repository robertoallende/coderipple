# CodeRipple Library

**Multi-Agent Documentation System Library**

The CodeRipple library provides sophisticated multi-agent documentation generation capabilities through AWS Strands orchestration and Amazon Bedrock AI enhancement. This library implements a layered documentation framework with intelligent agent coordination.

## Installation & Setup

### Prerequisites
```bash
# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
Set environment variables for optimal functionality:
```bash
# AWS Bedrock (optional - for AI enhancement)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# GitHub Integration (optional - for private repos)
export GITHUB_TOKEN=your_github_personal_access_token

# CodeRipple Configuration
export CODERIPPLE_SOURCE_REPO=/path/to/your/source/repo
export CODERIPPLE_OUTPUT_DIR=./documentation/output
export CODERIPPLE_MIN_QUALITY_SCORE=70
```

## Usage

### 1. Run the Complete System
```bash
# Main entry point - runs complete multi-agent system
python run_coderipple.py
```

### 2. Test Individual Components
```bash
# Test source code analysis
python src/source_code_analysis_tool.py

# Test existing content discovery
python src/existing_content_discovery_tool.py

# Test individual agents
python src/tourist_guide_agent.py
python src/building_inspector_agent.py
python src/historian_agent.py
python src/orchestrator_agent.py
```

### 3. Run With Sample Data
```bash
# Test webhook processing
python examples/test_webhook.py examples/sample.json push

# Test with diff fetching (requires internet)
python examples/test_webhook.py examples/sample.json push --fetch-diff

# For private repositories
export GITHUB_TOKEN=your_github_personal_access_token
python examples/test_webhook.py examples/sample.json push --fetch-diff
```

### 4. Testing & Validation
```bash
# Run all tests (comprehensive test suite)
./run_tests.sh

# Run specific test suites
python -m unittest tests.test_source_code_analysis_tool -v
python -m unittest tests.test_existing_content_discovery_tool -v
python -m unittest tests.test_tourist_guide_agent -v
python -m unittest tests.test_building_inspector_agent -v
python -m unittest tests.test_historian_agent -v
```

## Multi-Agent Architecture

### Agent Roles

#### **Orchestrator Agent**
- Receives webhook data from GitHub
- Uses git analysis tool to understand code changes
- Applies Layer Selection Decision Tree to determine which agents to invoke
- Coordinates responses from specialist agents

#### **Tourist Guide Agent** (How to ENGAGE)
- **Role**: Shows visitors around the system, explains how to get started
- **Responsibilities**: Discovery guides, Getting Started tutorials, Common Patterns, Troubleshooting
- **Update Pattern**: Task-oriented updates based on user feedback and workflow changes

#### **Building Inspector Agent** (What it IS)
- **Role**: Documents what's actually there right now, current specifications
- **Responsibilities**: Architecture & Design, Interfaces & Usage, Current Capabilities, Technology Stack
- **Update Pattern**: Incremental rewrites - sections updated as they change

#### **Historian Agent** (Why it BECAME this way)
- **Role**: Preserves the story of why things were built this way, maintains institutional memory
- **Responsibilities**: ADRs, Problem Evolution, Major Refactors, Technology Migrations
- **Update Pattern**: Append-only - new decisions added, old ones preserved with version context

### Agent Coordination
```
GitHub Changes → Orchestrator → Layer Selection Decision Tree → Specialist Agents → Coordinated Documentation
```

## Core Features

### ✅ **Source Code Analysis**
- Understands project structure, APIs, technologies, and purpose
- Intelligent diff analysis for targeted documentation updates
- Technology stack detection and capability assessment

### ✅ **Existing Content Discovery**
- Reads and analyzes current documentation state
- Identifies gaps and improvement opportunities
- Maintains documentation continuity and context

### ✅ **Context-Aware Content Generation**
- AI-enhanced content creation (not generic templates)
- Context-aware updates based on actual code changes
- Cross-agent coordination for comprehensive coverage

### ✅ **Content Validation Pipeline**
- Quality scoring and enforcement with comprehensive checks
- Progressive quality standards with fallback strategies
- Alignment between Bedrock enhancement and validation systems

### ✅ **Amazon Bedrock Integration**
- AI-powered content enhancement and consistency checking
- Quality measurement alignment across systems
- Iterative improvement with targeted feedback loops

## Configuration Options

### Environment Variables
- `CODERIPPLE_SOURCE_REPO`: Path to source repository (default: current directory)
- `CODERIPPLE_OUTPUT_DIR`: Documentation output directory (default: `./coderipple/`)
- `CODERIPPLE_ENABLED_AGENTS`: Comma-separated list of agents to enable
- `CODERIPPLE_MIN_QUALITY_SCORE`: Minimum quality score threshold (default: 70)
- `CODERIPPLE_MAX_RETRIES`: Maximum enhancement retry attempts (default: 3)

### Quality Pipeline Configuration
```python
# Quality tiers and thresholds
QUALITY_TIERS = {
    'high': 85,      # High-quality content threshold
    'medium': 70,    # Medium-quality content threshold  
    'basic': 50      # Basic content threshold
}
```

## API Reference

### Core Tools

#### Git Analysis Tool
```python
@tool
def analyze_git_changes(git_diff: str, change_type: str) -> dict:
    """Extract specific changes for targeted documentation"""
```

#### Content Generation Tool
```python
@tool
def generate_context_aware_content(section: str, git_analysis: dict, file_changes: list):
    """Generate content based on actual changes rather than generic templates"""
```

#### Cross-Agent Context Tool
```python
def share_agent_context(agent_results: dict, conversation_state: dict):
    """Make agent outputs available to subsequent agents"""
```

### Data Structures

#### CommitInfo
```python
@dataclass
class CommitInfo:
    sha: str
    message: str
    author: str
    timestamp: str
    files_changed: List[str]
```

#### DocumentationUpdate
```python
@dataclass
class DocumentationUpdate:
    section: str
    content: str
    update_type: str  # 'create', 'update', 'append'
    quality_score: float
```

## Testing

### Test Coverage
- **82+ comprehensive tests** covering all components
- Unit tests for each agent and tool
- Integration tests for multi-agent workflows
- Content quality validation tests
- AWS Bedrock integration tests (with mocking)

### Test Categories
- **Source Code Analysis**: Project structure understanding
- **Content Generation**: Context-aware documentation creation
- **Agent Coordination**: Multi-agent workflow validation
- **Quality Pipeline**: Content validation and scoring
- **Bedrock Integration**: AI-enhanced content generation

## Troubleshooting

### Common Issues

#### Quality Pipeline Failures
```bash
# Check quality alignment
python src/quality_alignment_tools.py

# Debug validation pipeline
python debug_validation.py
```

#### AWS Bedrock Connection Issues
```bash
# Test Bedrock connectivity
python examples/simple_bedrock_demo.py

# Use mock for testing
python examples/test_bedrock_mock_demo.py
```

#### Agent Coordination Problems
```bash
# Test agent context flow
python -m unittest tests.test_agent_context_flow -v

# Debug orchestrator logic
python src/orchestrator_agent.py --debug
```

## Development

### Code Structure
```
src/
├── agents/                 # Agent implementations
│   ├── orchestrator_agent.py
│   ├── tourist_guide_agent.py
│   ├── building_inspector_agent.py
│   └── historian_agent.py
├── tools/                  # Strands @tool functions
│   ├── git_analysis_tool.py
│   ├── content_generation_tools.py
│   └── bedrock_integration_tools.py
└── utils/                  # Utility functions
    ├── config.py
    └── webhook_parser.py
```

### Key Patterns
- **Multi-Agent Architecture**: AWS Strands @tool decorators for coordination
- **AI Integration**: Amazon Bedrock for content enhancement
- **Context Flow**: Cross-agent state sharing and capability referencing
- **Quality Assurance**: Comprehensive validation pipeline with scoring
- **Dataclasses**: Structured data handling (`CommitInfo`, `WebhookEvent`, `AgentContext`)

### Extending the System

#### Adding New Agents
1. Create agent class inheriting from base agent pattern
2. Define agent role and responsibilities
3. Implement Strands @tool functions
4. Add agent to orchestrator decision tree
5. Write comprehensive tests

#### Adding New Tools
1. Define tool function with @tool decorator
2. Add proper type hints and documentation
3. Integrate with existing agent workflows
4. Add validation and error handling
5. Write unit tests

---

*CodeRipple Library: Intelligent multi-agent documentation generation for modern software projects.*