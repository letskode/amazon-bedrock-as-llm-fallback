#!/usr/bin/env python3
import os
import time
from typing import List, Dict, Tuple, Optional, Any

from litellm import completion, APIError, RateLimitError, APIConnectionError, AuthenticationError

"""
LiteLLM-based fallback router with OpenAI -> Anthropic -> Bedrock fallback chain

- Primary: OpenAI models
- Fallback 1: Anthropic direct API
- Fallback 2: Bedrock models (Claude, Llama, etc.)
- Supports model-to-model fallback within Bedrock

Uses the same router mapping style as openai_bedrock_openweight_fallback.py
"""

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass

REQUEST_TIMEOUT: float = 60.0

# Import centralized router configuration
from router_config import LITELLM_ROUTER_MAPPING

ROUTER_STYLE_MAPPING = LITELLM_ROUTER_MAPPING


def _get_model_config(model_name: str) -> Dict[str, Any]:
    """Get model configuration by model_name from ROUTER_STYLE_MAPPING."""
    model_list = ROUTER_STYLE_MAPPING["model_list"]
    for entry in model_list:
        if entry.get("model_name") == model_name:
            return entry
    raise ValueError(f"Model '{model_name}' not found in ROUTER_STYLE_MAPPING")


def _get_fallback_chain(primary_model: str) -> List[str]:
    """Get fallback chain for a primary model."""
    fallbacks = ROUTER_STYLE_MAPPING["fallbacks"]
    for rule in fallbacks:
        if primary_model in rule:
            return rule[primary_model]
    return []


def _build_litellm_model_string(config: Dict[str, Any]) -> str:
    """Build LiteLLM model string from config."""
    provider = config.get("litellm_provider")
    params = config.get("params", {})
    model = params.get("model")
    
    if provider == "bedrock":
        region = params.get("aws_region_name", "us-east-1")
        return f"bedrock/{model}"
    elif provider == "anthropic":
        return f"anthropic/{model}"
    elif provider == "openai":
        return model
    else:
        return model


def litellm_completion_with_fallback(
    messages: List[Dict[str, str]],
    primary_model_name: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    attempt_fallback: bool = True,
) -> Tuple[str, str]:
    """
    Execute LiteLLM completion with automatic fallback chain.
    
    Returns (provider_label, response_text)
    """
    # Build fallback chain starting with primary
    fallback_chain = [primary_model_name] + _get_fallback_chain(primary_model_name)
    
    last_error = None
    
    for model_name in fallback_chain:
        try:
            config = _get_model_config(model_name)
            litellm_model = _build_litellm_model_string(config)
            provider = config.get("litellm_provider", "unknown")
            
            # Prepare completion kwargs
            completion_kwargs = {
                "model": litellm_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": REQUEST_TIMEOUT,
            }
            
            # Add provider-specific parameters
            params = config.get("params", {})
            if provider == "bedrock" and "aws_region_name" in params:
                completion_kwargs["aws_region_name"] = params["aws_region_name"]
            elif provider in ["openai", "anthropic"] and "api_key" in params:
                completion_kwargs["api_key"] = params["api_key"]
            
            # Retry logic for transient errors
            for attempt in range(3):
                try:
                    response = completion(**completion_kwargs)
                    provider_label = f"{provider}:{params.get('model', litellm_model)}"
                    return provider_label, response.choices[0].message.content or ""
                    
                except (RateLimitError, APIConnectionError) as e:
                    if attempt < 2:  # Retry transient errors
                        time.sleep(0.5 * (2 ** attempt))
                        continue
                    raise e
                    
        except Exception as e:
            last_error = e
            if not attempt_fallback or model_name == fallback_chain[-1]:
                break
            continue
    
    # If we get here, all models failed
    raise last_error or RuntimeError("All fallback models failed")


def AIAssistant(
    question: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    primary_model: str = "openai-gpt4o",
) -> Tuple[str, str]:
    """
    Main entry point for AI completion with fallback.
    
    Args:
        question: User question
        system_prompt: System prompt (optional)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        primary_model: Primary model name from ROUTER_STYLE_MAPPING
        
    Returns:
        Tuple of (provider_label, response_text)
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})
    
    return litellm_completion_with_fallback(
        messages=messages,
        primary_model_name=primary_model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


# Example usage
if __name__ == "__main__":
    try:
        provider, response = AIAssistant(
            question="What is the capital of France?",
            system_prompt="You are a helpful assistant.",
            primary_model="anthropic-claude-4"
        )
        print(f"Provider: {provider}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")