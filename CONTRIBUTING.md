# Contributing to LLM Fallback Router

Thanks for your interest in contributing! This project provides production-ready LLM fallback routers for automatic failover between AI model providers.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/llm-fallback-router.git
   cd llm-fallback-router
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and AWS credentials
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Test individual routers
   python test_litellm_fallback.py
   python test_bedrock_converse_fallback.py
   
   # Test specific implementations
   python litellm_fallback_router.py
   python bedrock_converse_fallback.py
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and modular
- Use meaningful variable names

## Testing

- Add tests for new router implementations
- Test fallback chains thoroughly
- Include error handling tests
- Test with different model configurations

## Areas for Contribution

### High Priority
- **Async Support**: Add async versions of routers for better performance
- **Observability**: Add structured logging and metrics collection
- **Circuit Breaker**: Implement circuit breaker pattern for failed providers
- **Response Caching**: Add caching for repeated queries

### Medium Priority
- **Load Balancing**: Add weighted routing for cost/performance optimization
- **Streaming Support**: Add streaming response support
- **Model Benchmarking**: Add performance comparison tools
- **Configuration Validation**: Add config validation and better error messages

### Documentation
- **Examples**: More real-world usage examples
- **Tutorials**: Step-by-step integration guides
- **Best Practices**: Production deployment guides
- **Troubleshooting**: Common issues and solutions

## Router Implementation Guidelines

When adding new router implementations:

1. **Follow the pattern**: Use the same interface as existing routers
2. **Centralized config**: Add configuration to `router_config.py`
3. **Error handling**: Include comprehensive error handling and retry logic
4. **Fallback chains**: Support automatic fallback with configurable chains
5. **Testing**: Add corresponding test file
6. **Documentation**: Update README with new router details

## Submitting Issues

When submitting issues:
- Use clear, descriptive titles
- Include steps to reproduce
- Provide error messages and logs
- Specify your environment (Python version, OS, etc.)
- Include relevant configuration (without API keys)

## Questions?

Feel free to open an issue for questions about:
- Architecture decisions
- Implementation approaches
- Integration patterns
- Best practices

## License

By contributing, you agree that your contributions will be licensed under the MIT License.