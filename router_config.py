#!/usr/bin/env python3
"""
Centralized Router Configuration

This module contains all router mappings used across different fallback implementations.
All fallback routers (LiteLLM, Bedrock Converse, OpenAI) import from this single source.
"""
import os
from typing import Dict, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass

# LiteLLM Router Configuration
LITELLM_ROUTER_MAPPING: Dict[str, Any] = {
    "model_list": [
        # Anthropic direct - Claude 4 and 3.7 models
        {
            "model_name": "anthropic-claude-4",
            "litellm_provider": "anthropic",
            "params": {
                "model": "claude-4-20250115",
                "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "rpm": 40,
            },
        },
        {
            "model_name": "anthropic-claude-sonnet-37",
            "litellm_provider": "anthropic",
            "params": {
                "model": "claude-3-7-sonnet-20250115",
                "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "rpm": 50,
            },
        },
        {
            "model_name": "anthropic-claude-haiku-37",
            "litellm_provider": "anthropic",
            "params": {
                "model": "claude-3-7-haiku-20250115",
                "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "rpm": 60,
            },
        },
        # Bedrock models - Claude 4, 3.7, and Llama Maverick
        {
            "model_name": "bedrock-claude-4",
            "litellm_provider": "bedrock",
            "params": {
                "model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 30,
            },
        },
        {
            "model_name": "bedrock-claude-sonnet-37",
            "litellm_provider": "bedrock",
            "params": {
                "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 40,
            },
        },
        {
            "model_name": "bedrock-claude-haiku-37",
            "litellm_provider": "bedrock",
            "params": {
                "model": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 50,
            },
        },
        {
            "model_name": "bedrock-llama-maverick",
            "litellm_provider": "bedrock",
            "params": {
                "model": "us.meta.llama4-maverick-17b-instruct-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-west-2"),
                "rpm": 30,
            },
        },
        # OpenAI models
        {
            "model_name": "openai-gpt4o",
            "litellm_provider": "openai",
            "params": {
                "model": "gpt-4o",
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "rpm": 60,
            },
        },
    ],
    "fallbacks": [
        {"anthropic-claude-4": ["bedrock-claude-4", "bedrock-claude-sonnet-37"]},
        {"anthropic-claude-sonnet-37": ["bedrock-claude-sonnet-37", "bedrock-claude-haiku-37"]},
        {"anthropic-claude-haiku-37": ["bedrock-claude-haiku-37", "bedrock-llama-maverick"]},
        {"bedrock-claude-4": ["bedrock-claude-sonnet-37", "bedrock-llama-maverick"]},
        {"bedrock-claude-sonnet-37": ["bedrock-claude-haiku-37", "bedrock-llama-maverick"]},
        {"bedrock-claude-haiku-37": ["bedrock-llama-maverick"]},
        {"openai-gpt4o": ["anthropic-claude-4", "bedrock-claude-4"]},
    ],
}

# Bedrock Converse Router Configuration
BEDROCK_CONVERSE_ROUTER_MAPPING: Dict[str, Any] = {
    "model_list": [
        {
            "model_name": "bedrock-claude-4",
            "params": {
                "model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 30,
            },
        },
        {
            "model_name": "bedrock-claude-sonnet-37",
            "params": {
                "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 40,
            },
        },
        {
            "model_name": "bedrock-claude-sonnet-35",
            "params": {
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 50,
            },
        },
        {
            "model_name": "bedrock-claude-haiku",
            "params": {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-east-1"),
                "rpm": 60,
            },
        },
        {
            "model_name": "bedrock-llama-maverick",
            "params": {
                "model": "us.meta.llama4-maverick-17b-instruct-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-west-2"),
                "rpm": 30,
            },
        },
        {
            "model_name": "bedrock-llama3-70b",
            "params": {
                "model": "meta.llama3-70b-instruct-v1:0",
                "aws_region_name": os.environ.get("AWS_REGION", "us-west-2"),
                "rpm": 25,
            },
        },
    ],
    "fallbacks": [
        {"bedrock-claude-4": ["bedrock-claude-sonnet-37", "bedrock-claude-sonnet-35"]},
        {"bedrock-claude-sonnet-37": ["bedrock-claude-sonnet-35", "bedrock-claude-haiku"]},
        {"bedrock-claude-sonnet-35": ["bedrock-claude-haiku", "bedrock-llama-maverick"]},
        {"bedrock-claude-haiku": ["bedrock-llama-maverick", "bedrock-llama3-70b"]},
        {"bedrock-llama-maverick": ["bedrock-llama3-70b"]},
    ],
}

# OpenAI + Bedrock OpenAI-compatible Router Configuration
OPENAI_BEDROCK_ROUTER_MAPPING: Dict[str, Any] = {
    "model_list": [
        # OpenAI models
        {
            "model_name": "openai-gpt4o",
            "params": {
                "model": "gpt-4o",
                "api_base": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "rpm": 60,
            },
        },
        # Bedrock models via OpenAI-compatible endpoint
        {
            "model_name": "bedrock-claude-4",
            "params": {
                "model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "api_base": os.environ.get("BEDROCK_OPENAI_BASE_URL", ""),
                "api_key": os.environ.get("BEDROCK_OPENAI_API_KEY", ""),
                "rpm": 30,
            },
        },
        {
            "model_name": "bedrock-claude-sonnet-37",
            "params": {
                "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "api_base": os.environ.get("BEDROCK_OPENAI_BASE_URL", ""),
                "api_key": os.environ.get("BEDROCK_OPENAI_API_KEY", ""),
                "rpm": 40,
            },
        },
        {
            "model_name": "bedrock-claude-haiku-37",
            "params": {
                "model": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                "api_base": os.environ.get("BEDROCK_OPENAI_BASE_URL", ""),
                "api_key": os.environ.get("BEDROCK_OPENAI_API_KEY", ""),
                "rpm": 50,
            },
        },
        {
            "model_name": "bedrock-llama-maverick",
            "params": {
                "model": "us.meta.llama4-maverick-17b-instruct-v1:0",
                "api_base": os.environ.get("BEDROCK_OPENAI_BASE_URL", ""),
                "api_key": os.environ.get("BEDROCK_OPENAI_API_KEY", ""),
                "rpm": 30,
            },
        },
    ],
    "fallbacks": [
        {"openai-gpt4o": ["bedrock-claude-4", "bedrock-claude-sonnet-37"]},
        {"bedrock-claude-4": ["bedrock-claude-sonnet-37", "bedrock-claude-haiku-37"]},
        {"bedrock-claude-sonnet-37": ["bedrock-claude-haiku-37", "bedrock-llama-maverick"]},
        {"bedrock-claude-haiku-37": ["bedrock-llama-maverick"]},
    ],
}