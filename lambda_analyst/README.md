# CodeRipple Magic Mirror 🪞

Intelligent code documentation generator that analyzes git repositories and creates comprehensive setup guides, architecture overviews, and project insights.

## Quick Start

### Prerequisites
- Python 3.10+
- Git installed
- AWS credentials configured (for Amazon Bedrock)

### Installation
```bash
pip install -r requirements.txt
```

### Test It
```bash
# Test on current directory (print to console)
python magic_mirror.py .

# Test and save to file
python magic_mirror.py . --output ./docs

# Test another repository and save
python magic_mirror.py /path/to/repository -o ./output

# With debug logging
LOG_LEVEL=DEBUG python magic_mirror.py . -o ./docs
```

### Expected Output
The Magic Mirror will generate markdown documentation covering:
- **Getting Started**: Setup instructions and prerequisites
- **Architecture**: Project structure and components  
- **Project Evolution**: Development activity and team insights

### How It Works
1. **Time-Aware Analysis**: Adapts depth based on 15-minute Lambda constraints
2. **Progressive Quality**: Getting Started → Architecture → Evolution
3. **Smart Tools**: Git analysis + file system exploration + time management
4. **Quality Loops**: Assesses and improves documentation iteratively

### AWS Lambda Deployment
Ready for Lambda deployment with CDK - see `lambda_sample/` in parent directory.

---
*"Mirror, mirror on the wall, tell me about this codebase, once and for all!"*