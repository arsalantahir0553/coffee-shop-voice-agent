import json
import re

import requests

from . import config

SYSTEM_TEMPLATE = """You are a friendly voice ordering assistant at {shop_name}, a coffee shop.
Take the customer's order conversationally. Only offer items from this menu:

{menu_text}

Standard questions to ask if not already answered: {standard_questions}

Current order so far:
{current_order}

Respond with ONLY a single JSON object, no other text, in this exact shape:
{{
  "reply": "<what to say out loud to the customer, natural and brief>",
  "add_items": [
    {{"drink": "<drink name>", "size": "<small/medium/large or null>", "hot_or_iced": "<hot/iced or null>", "milk": "<milk or null>", "add_ons": ["<add-on name>", "..."]}}
  ],
  "remove_last_item": false,
  "order_complete": false
}}
Leave "add_items" empty if the customer isn't adding anything new this turn.
Set "order_complete" to true only once the customer confirms the order is finished.
"""


def _extract_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def get_agent_turn(system_prompt, history, user_text):
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    response = requests.post(
        config.OLLAMA_URL,
        json={
            "model": config.OLLAMA_MODEL,
            "messages": messages,
            "format": "json",
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]
    parsed = _extract_json(content)

    if parsed is None:
        parsed = {}
    parsed.setdefault("reply", "Sorry, could you say that again?")
    parsed.setdefault("add_items", [])
    parsed.setdefault("remove_last_item", False)
    parsed.setdefault("order_complete", False)
    return parsed, content
