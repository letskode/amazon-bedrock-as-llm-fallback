# LLM Fallback Router Implementations

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)

A collection of production-ready LLM fallback router implementations that demonstrate automatic failover between different AI model providers (OpenAI, Anthropic, Amazon Bedrock) with consistent router-style configuration.

> **🚀 Zero-downtime AI operations during provider outages**

This project demonstrates how to use **Amazon Bedrock as a reliable foundation** for LLM applications, providing automatic failover when other providers experience outages.

## Business Problem

Major LLM providers including Anthropic, OpenAI, and Google Gemini have experienced multiple service outages since launch. Startups and enterprises relying on first-party APIs face significant operational risk during these disruptions, with no recovery options beyond waiting for service restoration.

**Key Challenges:**
- ❌ Single points of failure in production systems
- ❌ Revenue loss during provider outages
- ❌ Poor user experience during service disruptions
- ❌ No automated recovery mechanisms
- ❌ Vendor lock-in limiting flexibility

## Solution: Multi-Provider Fallback Strategy

This project provides a comprehensive fallback strategy that enables continuous operations during outages while promoting Amazon Bedrock adoption as a reliable foundation for enterprise AI applications.

**Benefits:**
- ✅ **Zero-downtime operations** during provider outages
- ✅ **Automatic failover** with intelligent retry logic
- ✅ **Reduced vendor lock-in** through provider abstraction
- ✅ **Cost optimization** through strategic model routing
- ✅ **Enhanced reliability** with multiple backup options
- ✅ **Bedrock-first architecture** for enterprise-grade stability
- ✅ **AWS-native integration** with IAM, CloudWatch, and VPC

## Architecture

This sample demonstrates a resilient AI architecture pattern:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Primary API   │───▶│  Fallback API   │───▶│  Amazon Bedrock │
│  (OpenAI/Anthropic) │    │  (Anthropic)    │    │   (Reliable)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Rate Limits              API Errors              Always Available
   Outages                  Auth Issues             Multi-Region
   Network Issues           Service Down            Enterprise SLAs
```

**Key AWS Services Used:**
- **Amazon Bedrock** - Foundation model hosting and inference
- **AWS IAM** - Secure access control and permissions
- **AWS CloudWatch** - Monitoring and observability (optional)
- **AWS VPC** - Network security (optional)

## Router Implementations

This project provides three different fallback router implementations:

1. **LiteLLM Router** - Multi-provider fallback using LiteLLM SDK
2. **Bedrock Converse Router** - Bedrock-native fallback using Converse API
3. **OpenAI + Bedrock Router** - OpenAI SDK with Bedrock OpenAI-compatible endpoint fallback

All implementations share the same router-style configuration pattern and support automatic failover with retry logic.

## Features

- ✅ **Multi-provider fallback**: OpenAI → Anthropic → Bedrock
- ✅ **Model-to-model fallback**: Within Bedrock (Claude 4 → Claude 3.7 → Llama)
- ✅ **Centralized configuration**: Single source of truth for all router mappings
- ✅ **Automatic retry**: Handles transient errors with exponential backoff
- ✅ **Production-ready**: Proper error handling, timeouts, and rate limiting
- ✅ **Consistent interface**: Same API across all implementations

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **AWS Account** with Bedrock access
3. **API Keys** (optional, for OpenAI/Anthropic direct access)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-fallback-router.git
cd llm-fallback-router

# Run setup script (recommended)
python setup.py

# Or manual setup:
pip install -r requirements.txt
cp .env.example .env
```

### Environment Setup

Edit `.env` file with your credentials:

```bash
# AWS Configuration (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key  # Optional if using IAM roles
AWS_SECRET_ACCESS_KEY=your_secret_key  # Optional if using IAM roles

# OpenAI (optional)
OPENAI_API_KEY=your_openai_key

# Anthropic (optional)
ANTHROPIC_API_KEY=your_anthropic_key

# Bedrock OpenAI-compatible endpoint (optional)
BEDROCK_OPENAI_BASE_URL=your_bedrock_openai_url
BEDROCK_OPENAI_API_KEY=your_bedrock_openai_key
```

### Basic Usage

```python
# LiteLLM Router (recommended)
from litellm_fallback_router import AIAssistant

provider, response = AIAssistant(
    question="What is machine learning?",
    primary_model="anthropic-claude-4"
)
print(f"Provider: {provider}")
print(f"Response: {response}")
```

## Router Implementations

### 1. LiteLLM Router (`litellm_fallback_router.py`)

**Best for**: Multi-provider environments with unified interface

```python
from litellm_fallback_router import AIAssistant

# Automatic fallback: Anthropic Claude 4 → Bedrock Claude 4 → Bedrock Claude 3.7
provider, response = AIAssistant(
    question="Explain quantum computing",
    system_prompt="You are a helpful assistant",
    primary_model="anthropic-claude-4",
    temperature=0.7,
    max_tokens=500
)
```

**Supported Providers:**
- Anthropic Direct API
- Amazon Bedrock
- OpenAI

### 2. Bedrock Converse Router (`bedrock_converse_fallback.py`)

**Best for**: AWS-native environments with Bedrock-only models

```python
from bedrock_converse_fallback import AIAssistant

# Bedrock-only fallback chain
provider, response = AIAssistant(
    question="What is AI?",
    primary_model="bedrock-claude-4"
)
```

**Supported Models:**
- Claude 4, Claude 3.7 Sonnet, Claude 3.5 Sonnet, Claude Haiku
- Llama 4 Maverick, Llama 3 70B

### 3. OpenAI + Bedrock Router (`openai_bedrock_openweight_fallback.py`)

**Best for**: OpenAI primary with Bedrock fallback via OpenAI-compatible endpoint

```python
from openai_bedrock_openweight_fallback import AIAssistant

# OpenAI → Bedrock via OpenAI-compatible interface
provider, response = AIAssistant(
    question="Hello world",
    openai_model="gpt-4o",
    use_fallback=False  # Set to True to force fallback
)
```

## Configuration

All routers use centralized configuration in `router_config.py`:

```python
# Example model configuration
{
    "model_name": "anthropic-claude-4",
    "litellm_provider": "anthropic",
    "params": {
        "model": "claude-4-20250115",
        "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "rpm": 40,
    },
}

# Example fallback chain
{"anthropic-claude-4": ["bedrock-claude-4", "bedrock-claude-sonnet-37"]}
```

### Customizing Fallback Chains

Edit `router_config.py` to modify:
- Model identifiers
- Fallback sequences
- Rate limits (RPM)
- AWS regions

## Testing

Run the test scripts to verify functionality:

```bash
# Test LiteLLM router
python3 test_litellm_fallback.py

# Test Bedrock Converse router
python3 test_bedrock_converse_fallback.py

# Test individual routers
python3 litellm_fallback_router.py
python3 bedrock_converse_fallback.py
```

## AWS Deployment

### Prerequisites

1. **AWS Account** with access to Amazon Bedrock
2. **AWS CLI** configured with appropriate credentials
3. **Python 3.8+** installed locally or on EC2/Lambda

### IAM Permissions

Create an IAM role/user with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude*",
                "arn:aws:bedrock:*::foundation-model/meta.llama*",
                "arn:aws:bedrock:*::foundation-model/us.anthropic.claude*",
                "arn:aws:bedrock:*::foundation-model/us.meta.llama*"
            ]
        }
    ]
}
```

### Bedrock Model Access

Enable model access in AWS Bedrock console:
1. Go to [AWS Bedrock console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access"
3. Request access for required models:
   - Anthropic Claude models (Claude 3.5 Sonnet, Claude 3.5 Haiku)
   - Meta Llama models (Llama 3.1, Llama 3.2)
   - US region models (us.anthropic.claude-*, us.meta.llama*)

### AWS Best Practices

**Security:**
- Use IAM roles instead of access keys when running on AWS services
- Enable AWS CloudTrail for API call auditing
- Use VPC endpoints for Bedrock access in production
- Implement least-privilege access policies

**Cost Optimization:**
- Monitor usage with AWS Cost Explorer
- Use cheaper models (Haiku) for simple tasks
- Implement request caching to reduce API calls
- Set up billing alerts for cost control

**Reliability:**
- Deploy across multiple AWS regions
- Use AWS Lambda for serverless scaling
- Implement circuit breakers for failed models
- Monitor with CloudWatch metrics and alarms

## Error Handling

All routers include comprehensive error handling:

- **Automatic retry** for transient errors (rate limits, network issues)
- **Fallback chain execution** when primary models fail
- **Detailed error messages** for debugging
- **Timeout protection** to prevent hanging requests

## Production Considerations

### Security
- Use IAM roles instead of access keys when possible
- Rotate API keys regularly
- Enable CloudTrail for audit logging
- Use VPC endpoints for Bedrock access

### Monitoring
- Monitor API usage and costs across providers
- Set up CloudWatch alarms for error rates
- Track fallback frequency to identify issues
- Log model performance metrics

### Cost Optimization
- Configure appropriate rate limits (RPM)
- Use cheaper models (Haiku) for simple tasks
- Implement response caching for repeated queries
- Monitor token usage across providers

## Troubleshooting

### Common Issues

**Import Error: `ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**AWS Credentials Error**
```bash
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**Bedrock Model Access Denied**
- Check IAM permissions
- Verify model access is enabled in Bedrock console
- Confirm model IDs are correct for your region

**API Key Issues**
- Verify API keys are set in `.env` file
- Check API key permissions and quotas
- Ensure keys are not expired

### Debug Mode

Enable debug logging:

```python
import litellm
litellm.set_verbose = True  # For LiteLLM router

import logging
logging.basicConfig(level=logging.DEBUG)  # For all routers
```

## File Structure

```
llm-fallback-router/
├── router_config.py              # Centralized router configuration
├── litellm_fallback_router.py    # LiteLLM multi-provider router
├── bedrock_converse_fallback.py  # Bedrock Converse API router
├── openai_bedrock_openweight_fallback.py  # OpenAI + Bedrock router
├── anthropic_to_bedrock_fallback.py  # Anthropic SDK with Bedrock fallback
├── litellm_multi_model.py        # Multi-model testing example
├── litellm_router_config_example.py  # Router configuration examples
├── test_litellm_fallback.py      # LiteLLM test script
├── test_bedrock_converse_fallback.py  # Bedrock test script
├── setup.py                      # Easy setup script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .github/                      # GitHub templates and workflows
├── CONTRIBUTING.md               # Contribution guidelines
├── SECURITY.md                   # Security policy
├── CHANGELOG.md                  # Version history
└── README.md                     # This file
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Review [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/)
- Open an [issue](../../issues) in the repository

## Star History

If this project helps you, please consider giving it a ⭐!