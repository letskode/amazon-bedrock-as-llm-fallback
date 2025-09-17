#!/usr/bin/env python3
"""
Test script for LiteLLM fallback router
"""
import os
from litellm_fallback_router import AIAssistant, ROUTER_STYLE_MAPPING

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass


def test_fallback_scenarios():
    """Test different fallback scenarios"""
    
    test_cases = [
        {
            "name": "Claude 4 Primary",
            "primary_model": "anthropic-claude-4",
            "question": "What is 2+2?",
        },
        {
            "name": "Claude Sonnet 3.7 Primary", 
            "primary_model": "anthropic-claude-sonnet-37",
            "question": "Explain quantum computing in one sentence.",
        },
        {
            "name": "Bedrock Llama Maverick Primary",
            "primary_model": "bedrock-llama-maverick", 
            "question": "What is the weather like today?",
        },
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        try:
            provider, response = AIAssistant(
                question=test_case["question"],
                system_prompt="You are a helpful assistant. Keep responses concise.",
                primary_model=test_case["primary_model"],
                temperature=0.3,
                max_tokens=100,
            )
            print(f"✅ Success with {provider}")
            print(f"Response: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Failed: {e}")


def show_router_config():
    """Display the current router configuration"""
    print("=== Router Configuration ===")
    print("\nModel List:")
    for model in ROUTER_STYLE_MAPPING["model_list"]:
        name = model["model_name"]
        provider = model["litellm_provider"]
        actual_model = model["params"]["model"]
        print(f"  {name}: {provider}/{actual_model}")
    
    print("\nFallback Chains:")
    for fallback_rule in ROUTER_STYLE_MAPPING["fallbacks"]:
        for primary, fallbacks in fallback_rule.items():
            print(f"  {primary} -> {' -> '.join(fallbacks)}")


if __name__ == "__main__":
    show_router_config()
    test_fallback_scenarios()