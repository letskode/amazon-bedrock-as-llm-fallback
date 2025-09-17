#!/usr/bin/env python3
"""
Example configuration for LiteLLM fallback router
Shows how to customize the router mapping for different use cases
"""
import os

# Example 1: Cost-optimized fallback (cheap -> expensive)
COST_OPTIMIZED_MAPPING = {
    "model_list": [
        {
            "model_name": "cheap-primary",
            "litellm_provider": "bedrock",
            "params": {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "aws_region_name": "us-east-1",
                "rpm": 100,
            },
        },
        {
            "model_name": "mid-tier",
            "litellm_provider": "openai",
            "params": {
                "model": "gpt-4o-mini",
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "rpm": 60,
            },
        },
        {
            "model_name": "premium",
            "litellm_provider": "anthropic",
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "rpm": 50,
            },
        },
    ],
    "fallbacks": [
        {"cheap-primary": ["mid-tier", "premium"]},
    ],
}

# Example 2: Performance-optimized fallback (fast -> reliable)
PERFORMANCE_OPTIMIZED_MAPPING = {
    "model_list": [
        {
            "model_name": "fast-primary",
            "litellm_provider": "openai",
            "params": {
                "model": "gpt-4o-mini",
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "rpm": 100,
            },
        },
        {
            "model_name": "reliable-fallback",
            "litellm_provider": "bedrock",
            "params": {
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "aws_region_name": "us-east-1",
                "rpm": 50,
            },
        },
    ],
    "fallbacks": [
        {"fast-primary": ["reliable-fallback"]},
    ],
}

# Example 3: Multi-region Bedrock fallback
MULTI_REGION_BEDROCK_MAPPING = {
    "model_list": [
        {
            "model_name": "bedrock-us-east",
            "litellm_provider": "bedrock",
            "params": {
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "aws_region_name": "us-east-1",
                "rpm": 50,
            },
        },
        {
            "model_name": "bedrock-us-west",
            "litellm_provider": "bedrock",
            "params": {
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "aws_region_name": "us-west-2",
                "rpm": 50,
            },
        },
        {
            "model_name": "bedrock-llama-fallback",
            "litellm_provider": "bedrock",
            "params": {
                "model": "meta.llama3-70b-instruct-v1:0",
                "aws_region_name": "us-west-2",
                "rpm": 30,
            },
        },
    ],
    "fallbacks": [
        {"bedrock-us-east": ["bedrock-us-west", "bedrock-llama-fallback"]},
    ],
}


def create_custom_router(mapping_config):
    """
    Example of how to use a custom mapping configuration
    """
    from litellm_fallback_router import litellm_completion_with_fallback
    
    # Temporarily replace the global mapping (in production, pass as parameter)
    import litellm_fallback_router
    original_mapping = litellm_fallback_router.ROUTER_STYLE_MAPPING
    litellm_fallback_router.ROUTER_STYLE_MAPPING = mapping_config
    
    try:
        messages = [{"role": "user", "content": "Hello, world!"}]
        primary_model = list(mapping_config["model_list"])[0]["model_name"]
        
        provider, response = litellm_completion_with_fallback(
            messages=messages,
            primary_model_name=primary_model,
        )
        return provider, response
    finally:
        # Restore original mapping
        litellm_fallback_router.ROUTER_STYLE_MAPPING = original_mapping


if __name__ == "__main__":
    print("Example router configurations:")
    print("\n1. Cost-optimized (Haiku -> GPT-4o-mini -> Claude Sonnet)")
    print("2. Performance-optimized (GPT-4o-mini -> Bedrock Claude)")  
    print("3. Multi-region Bedrock (US-East -> US-West -> Llama)")