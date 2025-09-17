# LiteLLM Fallback Router

A production-ready fallback system using LiteLLM that supports automatic failover between OpenAI, Anthropic, and Bedrock models.

## Features

- **Multi-provider fallback**: OpenAI → Anthropic → Bedrock
- **Model-to-model fallback**: Within Bedrock (Claude → Llama)
- **Router-style configuration**: Same mapping style as reference implementation
- **Automatic retry**: Handles transient errors with exponential backoff
- **Provider abstraction**: Unified interface across all providers

## Quick Start

```python
from litellm_fallback_router import AIAssistant

# Simple usage with automatic fallback
provider, response = AIAssistant(
    question="What is the capital of France?",
    system_prompt="You are a helpful assistant.",
    primary_model="openai-gpt4o"  # Falls back to Anthropic, then Bedrock
)

print(f"Provider: {provider}")
print(f"Response: {response}")
```

## Configuration

The router uses a mapping similar to the OpenAI reference implementation:

```python
ROUTER_STYLE_MAPPING = {
    "model_list": [
        {
            "model_name": "openai-gpt4o",
            "litellm_provider": "openai",
            "params": {
                "model": "gpt-4o",
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "rpm": 60,
            },
        },
        # ... more models
    ],
    "fallbacks": [
        {"openai-gpt4o": ["anthropic-claude-sonnet", "bedrock-claude-sonnet"]},
        # ... more fallback chains
    ],
}
```

## Supported Providers

### OpenAI
- Models: `gpt-4o`, `gpt-4o-mini`
- Requires: `OPENAI_API_KEY`

### Anthropic Direct
- Models: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`
- Requires: `ANTHROPIC_API_KEY`

### Amazon Bedrock
- Models: Claude, Llama, and other Bedrock-hosted models
- Requires: AWS credentials (IAM role or access keys)
- Supports: Multi-region fallback

## Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# AWS (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key  # Optional if using IAM roles
AWS_SECRET_ACCESS_KEY=your_secret_key  # Optional if using IAM roles
```

## Fallback Strategies

### 1. Cost-Optimized
Start with cheapest models, fallback to more expensive:
```
Bedrock Haiku → OpenAI GPT-4o-mini → Anthropic Claude Sonnet
```

### 2. Performance-Optimized  
Start with fastest models, fallback to most reliable:
```
OpenAI GPT-4o-mini → Bedrock Claude Sonnet
```

### 3. Multi-Region Bedrock
Fallback across AWS regions and models:
```
Bedrock US-East → Bedrock US-West → Bedrock Llama
```

## Error Handling

The router automatically handles:
- **Rate limiting**: Exponential backoff and retry
- **API errors**: Automatic fallback to next provider
- **Authentication errors**: Skip to next configured provider
- **Network issues**: Retry with timeout

## Testing

Run the test script to verify fallback functionality:

```bash
python test_litellm_fallback.py
```

This will test each provider and show the fallback chain in action.

## Comparison with Reference Implementation

| Feature | OpenAI Reference | LiteLLM Implementation |
|---------|------------------|----------------------|
| Provider Support | OpenAI + Bedrock OpenAI-compatible | OpenAI + Anthropic + Bedrock |
| Model Switching | Manual boolean flag | Automatic fallback chain |
| Configuration | Router-style mapping | Same router-style mapping |
| Error Handling | Basic retry | Advanced retry + fallback |
| SDK | OpenAI SDK only | LiteLLM (unified interface) |

## Production Considerations

1. **Rate Limits**: Configure `rpm` values based on your API limits
2. **Costs**: Monitor usage across providers in your observability dashboard
3. **Latency**: Test fallback chains to ensure acceptable response times
4. **Security**: Use IAM roles for Bedrock, rotate API keys regularly
5. **Monitoring**: Log provider usage and fallback frequency

## Integration with Bedrock-First Platform

This implementation integrates with the broader GenAI platform:

- **Observability**: Metrics flow to CloudWatch dashboard
- **Evaluations**: Use with Bedrock Evaluations for model selection
- **Prompts**: Compatible with Bedrock Prompt Management
- **Governance**: Works with agent-core policies and guardrails