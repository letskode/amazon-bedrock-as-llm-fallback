#!/usr/bin/env python3
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from anthropic import (
    Anthropic,
    AnthropicBedrock,
    APIError,
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

# Auto-load .env if present (no shell export needed)
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass

"""
Anthropic primary -> Bedrock Anthropic fallback (same model family), using Anthropic SDK only.

For fallback, use the official AnthropicBedrock client per docs, which authenticates via AWS
credentials (env/default providers) and aws_region.

Credentials via env:
- Primary: ANTHROPIC_API_KEY (optional ANTHROPIC_BASE_URL)
- Fallback: AWS creds via default providers; AWS_REGION (or AWS_DEFAULT_REGION)
"""

# Request timeout for Anthropic SDK calls (seconds)
REQUEST_TIMEOUT: float = 60.0

# Router-style mapping (primary anthropic model -> fallback bedrock model/profile)
ROUTER_STYLE_MAPPING: Dict[str, object] = {
    "model_list": [
        {
            "model_name": "anthropic-sonnet",
            "params": {
                "model": "claude-3-7-sonnet-latest",
                "rpm": 60,
            },
        },
        {
            "model_name": "bedrock-anthropic-sonnet",
            "params": {
                # Bedrock model id for Sonnet 3.7 per docs
                # https://docs.anthropic.com/en/api/claude-on-amazon-bedrock
                "bedrock_model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "aws_region": os.environ.get("AWS_REGION")
                or os.environ.get("AWS_DEFAULT_REGION")
                or "us-east-1",
                "rpm": 10,
            },
            
        },
        
    ],
    "fallbacks": [{"anthropic-sonnet": ["bedrock-anthropic-sonnet"]}],
}


def _resolve_by_anthropic_model_id(model_id: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    model_list = ROUTER_STYLE_MAPPING["model_list"]  # type: ignore[index]
    fallbacks = ROUTER_STYLE_MAPPING["fallbacks"]  # type: ignore[index]

    name_to_params: Dict[str, Dict[str, str]] = {}
    model_to_name: Dict[str, str] = {}
    for entry in model_list:  # type: ignore[assignment]
        mn = entry.get("model_name")
        params = entry.get("params")
        if isinstance(mn, str) and isinstance(params, dict):
            name_to_params[mn] = params  # type: ignore[assignment]
            m = params.get("model") or params.get("bedrock_model_id")
            if isinstance(m, str):
                model_to_name[m] = mn

    primary_name = model_to_name.get(model_id)
    if not primary_name:
        raise ValueError(f"Anthropic model '{model_id}' not found in ROUTER_STYLE_MAPPING")

    fallback_name: Optional[str] = None
    for rule in fallbacks:  # type: ignore[assignment]
        if primary_name in rule:
            lst = rule[primary_name]
            if isinstance(lst, list) and lst:
                fallback_name = lst[0]
                break
    if not fallback_name or fallback_name not in name_to_params:
        raise ValueError(f"No fallback configured for primary '{primary_name}'")

    return name_to_params[primary_name], name_to_params[fallback_name]


def _anthropic_messages_create(
    client: Anthropic,
    model: str,
    system_prompt: str,
    question: str,
    temperature: float,
    max_tokens: int,
) -> str:
    resp = client.messages.create(
        model=model,
        system=system_prompt or None,
        messages=[{"role": "user", "content": question}],
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=REQUEST_TIMEOUT,
    )
    # Anthropic SDK returns response with content list
    try:
        parts = resp.content or []
        texts = [p.text for p in parts if hasattr(p, "text")]
        return "".join(texts) if texts else ""
    except Exception:
        return str(resp)


def build_clients_and_models(
    anthropic_model: str,
    use_fallback: bool,
) -> Tuple[Optional[Anthropic], Optional[Dict[str, Any]], str, bool]:
    """Return (anthropic_client | None, bedrock_params | None, provider_label, is_fallback)."""
    primary_params, fallback_params = _resolve_by_anthropic_model_id(anthropic_model)

    if not use_fallback:
        api_key = (os.environ.get("ANTHROPIC_API_KEY", "")).strip()
        base_url = os.environ.get("ANTHROPIC_BASE_URL")  # usually None; Anthropic SDK has defaults
        client = Anthropic(api_key=api_key, base_url=base_url)
        model_to_use = primary_params.get("model", anthropic_model)
        return client, None, f"Anthropic:{model_to_use}", False

    # Fallback client uses AnthropicBedrock (uses AWS creds/default providers)
    region = fallback_params.get("aws_region") or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    fb_client = AnthropicBedrock(aws_region=region, aws_secret_key=aws_secret_key, aws_access_key=aws_access_key)
    bedrock_model_id = fallback_params.get("bedrock_model_id", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    return fb_client, {"model": bedrock_model_id}, f"AnthropicBedrock:{bedrock_model_id}", True


def AIAssistant(
    question: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    anthropic_model: str,
    use_fallback: bool,
) -> Tuple[str, str]:
    """Anthropic primary with automatic fallback to Bedrock for the same model family."""
    client, bedrock_params, provider_label, is_fallback = build_clients_and_models(
        anthropic_model=anthropic_model,
        use_fallback=use_fallback,
    )

    try:
        if not is_fallback and client is not None:
            # Simple retry/backoff for transient conditions on primary
            attempt = 0
            while True:
                try:
                    text = _anthropic_messages_create(
                        client=client,
                        model=anthropic_model,
                        system_prompt=system_prompt,
                        question=question,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return provider_label, text
                except (RateLimitError, APIConnectionError, APIError) as e:
                    status = getattr(e, "status_code", None)
                    transient = isinstance(e, APIConnectionError) or (status is not None and status >= 500) or isinstance(e, RateLimitError)
                    if attempt >= 2 or not transient:
                        raise
                    time.sleep(0.5 * (2 ** attempt))
                    attempt += 1
        else:
            assert bedrock_params is not None and client is not None
            text = _anthropic_messages_create(
                client=client,
                model=bedrock_params.get("model", anthropic_model),
                system_prompt=system_prompt,
                question=question,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return provider_label, text

    except (AuthenticationError, RateLimitError, NotFoundError, APIError, APIConnectionError) as e:
        # If primary failed and fallback not yet tried, try fallback once
        if not use_fallback:
            return AIAssistant(
                question=question,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                anthropic_model=anthropic_model,
                use_fallback=True,
            )
        raise


def main() -> None:
    # Parameters (no CLI args for simplicity; mirror other demo)
    QUESTION = "Where is my order and can I update my shipping address?"
    TEMPERATURE = 0.2
    MAX_TOKENS = 400
    USE_FALLBACK = False  # set True to use Bedrock fallback
    ANTHROPIC_MODEL = "claude-3-7-sonnet-latest"  # must exist in mapping

    system_prompt = (
        "You are a helpful, friendly customer service assistant. "
        "Answer concisely, with clear next steps. If policy or account access is required, explain what the user should do."
    )

    provider, text = AIAssistant(
        question=QUESTION,
        system_prompt=system_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        anthropic_model=ANTHROPIC_MODEL,
        use_fallback=USE_FALLBACK,
    )

    print("Provider:", provider)
    print("Question:", QUESTION)
    print("Answer:\n", text)


if __name__ == "__main__":
    main()


