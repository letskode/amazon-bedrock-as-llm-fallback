#!/usr/bin/env python3
import os
import time
import boto3
from typing import List, Dict, Tuple, Optional, Any
from botocore.exceptions import ClientError, BotoCoreError

"""
Bedrock Converse API fallback router

- Uses Bedrock Converse API for unified model interface
- Supports model-to-model fallback within Bedrock
- Same router mapping style as reference implementations
"""

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass

REQUEST_TIMEOUT: float = 60.0

# Import centralized router configuration
from router_config import BEDROCK_CONVERSE_ROUTER_MAPPING

ROUTER_STYLE_MAPPING = BEDROCK_CONVERSE_ROUTER_MAPPING


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


def _create_bedrock_client(region_name: str):
    """Create Bedrock runtime client."""
    return boto3.client('bedrock-runtime', region_name=region_name)


def bedrock_converse_with_fallback(
    messages: List[Dict[str, str]],
    primary_model_name: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    attempt_fallback: bool = True,
) -> Tuple[str, str]:
    """
    Execute Bedrock Converse API with automatic fallback chain.
    
    Returns (provider_label, response_text)
    """
    # Build fallback chain starting with primary
    fallback_chain = [primary_model_name] + _get_fallback_chain(primary_model_name)
    
    last_error = None
    
    for model_name in fallback_chain:
        try:
            config = _get_model_config(model_name)
            params = config.get("params", {})
            model_id = params.get("model")
            region = params.get("aws_region_name", "us-east-1")
            
            # Create client for this region
            client = _create_bedrock_client(region)
            
            # Prepare converse request
            converse_request = {
                "modelId": model_id,
                "messages": messages,
                "inferenceConfig": {
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                }
            }
            
            # Retry logic for transient errors
            for attempt in range(3):
                try:
                    response = client.converse(**converse_request)
                    
                    # Extract response text
                    output_message = response['output']['message']
                    response_text = ""
                    for content in output_message['content']:
                        if content['text']:
                            response_text += content['text']
                    
                    provider_label = f"bedrock:{model_id}"
                    return provider_label, response_text
                    
                except (ClientError, BotoCoreError) as e:
                    error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
                    if attempt < 2 and error_code in ['ThrottlingException', 'ServiceUnavailableException']:
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
    primary_model: str = "bedrock-claude-4",
) -> Tuple[str, str]:
    """
    Main entry point for Bedrock Converse API completion with fallback.
    
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
        messages.append({"role": "user", "content": [{"text": f"System: {system_prompt}\n\nUser: {question}"}]})
    else:
        messages.append({"role": "user", "content": [{"text": question}]})
    
    return bedrock_converse_with_fallback(
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
            primary_model="bedrock-claude-4"
        )
        print(f"Provider: {provider}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")