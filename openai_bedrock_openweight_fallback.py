#!/usr/bin/env python3
import os
import time
from typing import List, Dict, Tuple, Optional, Any

from openai import (
    OpenAI,
    APIError,
    RateLimitError,
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
)

"""
OpenAI primary with Bedrock OpenAI open-weight endpoint (OpenAI SDK only)

- Primary: standard OpenAI endpoint using OPENAI_API_KEY
- Fallback (when enabled): Bedrock OpenAI-compatible endpoint using BEDROCK_OPENAI_BASE_URL and BEDROCK_OPENAI_API_KEY
  Reference: https://aws.amazon.com/blogs/aws/openai-open-weight-models-now-available-on-aws/

Behavior:
- Use a single function that switches API base URL, API key, and model based on a boolean (use_fallback).
- No LiteLLM or boto3 is used; this is pure OpenAI SDK.
"""
# Load environment variables from a local .env file if present (no shell export required)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass

# NOTE: Set credentials via environment variables; do not hardcode secrets in code:
#  - OPENAI_API_KEY (and optional OPENAI_BASE_URL)
#  - BEDROCK_OPENAI_API_KEY, BEDROCK_OPENAI_BASE_URL

# Request timeout for OpenAI SDK calls (seconds)
REQUEST_TIMEOUT: float = 60.0

# (Using router-style mapping below. Simple MODEL_MAPPINGS removed.)

# Import centralized router configuration
from router_config import OPENAI_BEDROCK_ROUTER_MAPPING

ROUTER_STYLE_MAPPING = OPENAI_BEDROCK_ROUTER_MAPPING


def _resolve_by_openai_model_id(openai_model: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Given an OpenAI model id (e.g., 'gpt-4o'), return (primary_params, fallback_params)
    using ROUTER_STYLE_MAPPING by matching the primary entry whose params.model equals openai_model.
    """
    model_list = ROUTER_STYLE_MAPPING["model_list"]  # type: ignore[index]
    fallbacks = ROUTER_STYLE_MAPPING["fallbacks"]    # type: ignore[index]

    # Build indices
    name_to_params: Dict[str, Dict[str, str]] = {}
    model_to_name: Dict[str, str] = {}
    for entry in model_list:  # type: ignore[assignment]
        mn = entry.get("model_name")
        params = entry.get("params")
        if isinstance(mn, str) and isinstance(params, dict):
            name_to_params[mn] = params  # type: ignore[assignment]
            m = params.get("model")
            if isinstance(m, str):
                model_to_name[m] = mn

    primary_name = model_to_name.get(openai_model)
    if not primary_name:
        raise ValueError(f"OpenAI model '{openai_model}' not found in ROUTER_STYLE_MAPPING")

    # Find first fallback target for this primary name
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


def build_openai_client_and_model(
    openai_model: str,
    use_fallback: bool,
) -> Tuple[OpenAI, str, str, bool]:
    """Return (client, model_to_use, provider_label, is_fallback) using ROUTER_STYLE_MAPPING.

    Resolves api_base, api_key, and model for either primary (OpenAI) or fallback (Bedrock OpenAI-compatible).
    """
    primary_params, fallback_params = _resolve_by_openai_model_id(openai_model)

    if not use_fallback:
        api_key = (primary_params.get("api_key") or os.environ.get("OPENAI_API_KEY", "")).strip()
        primary_base = primary_params.get("api_base") or os.environ.get("OPENAI_BASE_URL")
        base_url = primary_base.strip() if isinstance(primary_base, str) and primary_base else None
        model_to_use = primary_params.get("model", openai_model)
        provider_label = f"OpenAI:{model_to_use}"
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model_to_use, provider_label, False

    # Fallback path (Bedrock OpenAI-compatible)
    api_key = (fallback_params.get("api_key") or os.environ.get("BEDROCK_OPENAI_API_KEY", "")).strip()
    fb_base = fallback_params.get("api_base") or os.environ.get("BEDROCK_OPENAI_BASE_URL", "")
    base_url = fb_base.strip() if isinstance(fb_base, str) and fb_base else None
    if not api_key or not base_url:
        raise RuntimeError("Missing BEDROCK_OPENAI_API_KEY or BEDROCK_OPENAI_BASE_URL for fallback.")
    model_to_use = fallback_params.get("model", openai_model)
    provider_label = f"BedrockOpenAI:{model_to_use}"
    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, model_to_use, provider_label, True


def AIAssistant(
    question: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    openai_model: str,
    use_fallback: bool,
) -> Tuple[str, str]:
    """Single entry: switch API key/base URL/model based on use_fallback via a helper.

    Returns (provider, text) where provider is "OpenAI:<model>" or "BedrockOpenAI:<model>".
    """
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})

    # Build client and model according to chosen path
    client, model_to_use, provider_label, is_fallback = build_openai_client_and_model(
        openai_model=openai_model,
        use_fallback=use_fallback,
    )
    try:
        req_kwargs: Dict[str, Any] = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature,
        }
        # Bedrock OpenAI-compatible endpoint expects max_completion_tokens
        if is_fallback:
            req_kwargs["max_completion_tokens"] = max_tokens
        else:
            req_kwargs["max_tokens"] = max_tokens

        # Simple retry for transient errors
        attempt = 0
        while True:
            try:
                resp = client.chat.completions.create(timeout=60.0, **req_kwargs)
                break
            except (RateLimitError, APIConnectionError, APIError) as e:
                status = getattr(e, "status_code", None)
                transient = isinstance(e, APIConnectionError) or (status is not None and status >= 500) or isinstance(e, RateLimitError)
                if attempt >= 2 or not transient:
                    raise
                time.sleep(0.5 * (2 ** attempt))
                attempt += 1

        return (provider_label, resp.choices[0].message.content or "")
    except (AuthenticationError, RateLimitError, NotFoundError, APIError, APIConnectionError) as e:
        # If primary fails with these errors, auto-switch to fallback.
        if not use_fallback:
            return AIAssistant(
                question=question,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_model=openai_model,
                use_fallback=True,
            )
        # Already on fallback -> exit with error
        raise





def _resolve_router_style(models: List[Dict[str, object]], fallbacks: List[Dict[str, List[str]]], primary_name: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Return (primary_params, fallback_params) from router-style mapping given a primary model_name."""
    name_to_params: Dict[str, Dict[str, str]] = {}
    for entry in models:
        mn = entry.get("model_name")  # type: ignore[assignment]
        params = entry.get("params")  # type: ignore[assignment]
        if isinstance(mn, str) and isinstance(params, dict):
            name_to_params[mn] = params  # type: ignore[assignment]
    fallback_target: Optional[str] = None
    for rule in fallbacks:
        if primary_name in rule:
            lst = rule[primary_name]
            if isinstance(lst, list) and lst:
                fallback_target = lst[0]
                break
    if primary_name not in name_to_params or not fallback_target or fallback_target not in name_to_params:
        raise ValueError("Invalid router-style mapping or primary_name not found")
    return name_to_params[primary_name], name_to_params[fallback_target]


def main() -> None:
    # -------- Parameters as variables (no CLI args) --------
    QUESTION = "Where is my order and can I update my shipping address?"
    TEMPERATURE = 0.2
    MAX_TOKENS = 400
    USE_FALLBACK = False  # set True to use Bedrock OpenAI-compatible fallback
    #OPENAI_MODEL = "gpt-4o-mini"  # must exist in ROUTER_STYLE_MAPPING primary params
    OPENAI_MODEL = "gpt-4o"  # must exist in ROUTER_STYLE_MAPPING primary params

    system_prompt = (
        "You are a helpful, friendly customer service assistant. "
        "Answer concisely, with clear next steps. If policy or account access is required, explain what the user should do."
    )

    provider, text = AIAssistant(
        question=QUESTION,
        system_prompt=system_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        openai_model=OPENAI_MODEL,
        use_fallback=USE_FALLBACK,
    )

    print("Provider:", provider)
    print("Question:", QUESTION)
    print("Answer:\n", text)


if __name__ == "__main__":
    main()
