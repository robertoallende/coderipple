# Troubleshooting

## Common Issues

### Setup and Installation

**Symptoms**: CodeRipple fails to start or import errors occur

**Possible Causes**:
- Virtual environment not activated
- Missing dependencies (4 packages required)
- Wrong working directory

**Solutions**:
1. **Verify Environment Setup**:
   ```bash
   source venv/bin/activate
   pip list | grep strands  # Should show strands-agents package
   ```

2. **Check Working Directory**:
   ```bash
   ls src/  # Should show agent modules
   python run_coderipple.py  # Run from project root
   ```

3. **Reinstall Dependencies**:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```
### Virtual Environment Issues

**Symptoms**: Import errors or missing dependencies

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation
which python  # Should point to venv/bin/python

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### Module Import Issues

**Symptoms**: `ModuleNotFoundError` for CodeRipple components

**Common Issues**:
- Running from wrong directory
- Virtual environment not activated
- Missing dependencies

**Solutions**:
```bash
# Run from project root directory
cd /path/to/coderipple

# Verify key modules exist
ls src/__init__.py

# Test imports
python -c "from src.__init__ import *"
```

### Documentation Generation Issues

**Symptoms**: No documentation files created in `coderipple/` directory

**Diagnostic Steps**:
```bash
# 1. Test bootstrap functionality
python -c "from src.tourist_guide_agent import bootstrap_user_documentation; print(bootstrap_user_documentation())"

# 2. Check file permissions
ls -la coderipple/

# 3. Verify agent execution
python run_coderipple.py --verbose
```

**Common Solutions**:
- Ensure `coderipple/` directory is writable
- Check that agent modules can import successfully
- Verify git repository has commits to analyze

### Content Quality Issues

**Symptoms**: Generated documentation is generic or inaccurate

**Possible Causes**:
- Insufficient project context analysis
- Agent prompts need customization
- Git analysis not capturing project-specific patterns

**Solutions**:
1. **Enhance Project Context**:
   ```python
   # Test context analysis
   from src.tourist_guide_agent import analyze_project_context_for_content_generation
   context = analyze_project_context_for_content_generation()
   print(context)
   ```

2. **Customize Agent Behavior**: Modify prompts in `src/` directory
3. **Validate Git Analysis**: Ensure change analysis captures relevant patterns

### AWS Integration Issues

**Symptoms**: Bedrock integration fails or AWS-related errors

**Possible Causes**:
- Missing AWS credentials
- Insufficient IAM permissions
- Region configuration issues

**Solutions**:
```bash
# Check AWS configuration
aws configure list

# Test Bedrock access
python examples/test_bedrock_demo.py

# Verify IAM permissions for Bedrock
aws bedrock list-foundation-models
```

## Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Run with debug output
python run_coderipple.py --debug

# Test individual components
python src/webhook_parser.py --verbose
python examples/test_git_agent.py
```

## Performance Optimization

### Large Repository Handling

For repositories with extensive history or large diffs:

```bash
# Process specific commits only
python run_coderipple.py --commits HEAD~5..HEAD

# Limit diff analysis scope
python run_coderipple.py --max-files 50
```

### Memory and Processing Issues

**Symptoms**: High memory usage or timeout errors

**Solutions**:
- Process commits in smaller batches
- Increase system memory allocation
- Configure agent timeout limits

## Getting Help

**Diagnostic Information to Collect**:
1. **System Environment**:
   ```bash
   python --version
   pip list | grep -E "(strands|boto3|pydantic)"
   ls -la src/
   ```

2. **Error Logs**: Copy full error messages and stack traces
3. **Project Context**: Repository size, commit frequency, existing documentation

**Support Channels**:
- **Documentation Issues**: Review this troubleshooting guide
- **Bug Reports**: Include diagnostic information above
- **Feature Requests**: Describe your specific documentation needs

## Known Limitations

- **Large Repositories**: Repositories with >10,000 commits may require performance tuning
- **Complex Merge Conflicts**: Manual resolution may be needed for conflicting documentation updates
- **AWS Service Limits**: Rate limits may affect high-frequency usage (>100 commits/hour)
- **Language Support**: Optimized for Python projects; other languages may need custom configuration

*This documentation is automatically maintained and updated as the system evolves.*
