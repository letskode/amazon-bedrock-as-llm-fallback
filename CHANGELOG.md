# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of LLM Fallback Router implementations
- LiteLLM multi-provider fallback router
- Bedrock Converse API fallback router  
- OpenAI + Bedrock OpenAI-compatible endpoint router
- Centralized router configuration system
- Comprehensive test scripts
- Production-ready error handling and retry logic
- Support for multiple AI model providers (OpenAI, Anthropic, Bedrock)
- Automatic model-to-model fallback within providers
- Environment-based configuration management
- Detailed documentation and usage examples

### Features
- ✅ Multi-provider fallback: OpenAI → Anthropic → Bedrock
- ✅ Model-to-model fallback within Bedrock (Claude → Llama)
- ✅ Centralized configuration with router-style mapping
- ✅ Automatic retry with exponential backoff
- ✅ Production-ready error handling and timeouts
- ✅ Consistent interface across all implementations
- ✅ Support for Claude 4, Claude 3.7, Llama Maverick models
- ✅ AWS multi-region support
- ✅ Rate limiting and cost optimization features

## [1.0.0] - 2025-01-XX

### Added
- Initial public release