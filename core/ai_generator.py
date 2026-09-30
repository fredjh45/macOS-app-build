"""
AI Content Generator for Google Sites Poster
Supports DeepSeek API and Grok (xAI) API.
Outputs structured JSON content strictly following the chosen PostStructure.
Enforces the rule: NO phone numbers or WhatsApp links in content body.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
from database.db import get_setting
from core.structures import PostStructure, get_structure_by_id

logger = logging.getLogger(__name__)

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"
GROK_ENDPOINT = "https://api.x.ai/v1/chat/completions"

def build_system_prompt(structure: Any) -> str:
    elements = getattr(structure, "elements", [])
    elements_desc = "\n".join([f"- {el.element_type}: key='{el.key}', label='{el.default_text}'" for el in elements]) if elements else "- Structured Local Business Landing Page"
    
    prompt = f"""You are an elite SEO copywriter and web layout architect for Google Sites.
You will receive a target Keyword and must generate structured content matching this layout structure:
{elements_desc}

CRITICAL RULES:
1. DO NOT include any phone numbers, telephone digits, mobile numbers, WhatsApp numbers, or WhatsApp links in any part of the generated text content. (Buttons will be dynamically injected with links separately).
2. Write engaging, high-ranking, natural, and persuasive content tailored to the Keyword.
3. Every H2 heading must be descriptive, authoritative, and include keyword variations.
4. Output MUST be valid JSON only. Do not include markdown code block formatting like ```json or ```. Return pure JSON.
5. page_title LENGTH RULE: 'page_title' (and 'h1_title' if present) MUST be STRICTLY between 60 and 70 characters long (including spaces). Never make it shorter than 60 or longer than 70 characters.

The JSON schema must follow:
{{
    "page_title": "Engaging Page Title",
    "header_tagline": "Catchy header banner subtitle",
    "sections": [
        {{
            "key": "section_key",
            "h2_heading": "Descriptive H2 Heading",
            "body_text": "Detailed multi-sentence content or bullet points...",
            "image_caption": "Optional short caption"
        }}
    ],
    "map_query": "A relevant major city or region associated with the topic",
    "footer_text": "Professional disclaimer and copyright note"
}}
"""
    return prompt

def generate_ai_content(
    keyword: str,
    structure_id: str,
    override_api_key: Optional[str] = None,
    override_provider: Optional[str] = None
) -> Dict[str, Any]:
    structure = get_structure_by_id(structure_id)
    provider = override_provider or get_setting("active_ai_provider", "deepseek").lower()
    
    if "grok" in provider:
        api_key = override_api_key or get_setting("grok_api_key", "")
        endpoint = GROK_ENDPOINT
        model = "grok-4.3"
    else:
        api_key = override_api_key or get_setting("deepseek_api_key", "")
        endpoint = DEEPSEEK_ENDPOINT
        model = "deepseek-chat"

    if not api_key:
        logger.warning(f"No API key configured for {provider}. Using rich fallback template.")
        return generate_fallback_content(keyword, structure)

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    s_id = getattr(structure, 'STRUCTURE_ID', getattr(structure, 'id', structure_id))
    s_name = getattr(structure, 'STRUCTURE_NAME', getattr(structure, 'name', structure_id))
    user_message = f"Target Keyword: {keyword}\nLayout Structure ID: {s_id} ({s_name})\nGenerate complete, structured website content now."

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_system_prompt(structure)},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 2500
    }
    if "grok" in provider:
        payload["reasoning_effort"] = "none"

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            content_text = result["choices"][0]["message"]["content"].strip()
            # Clean possible markdown wrapping
            if content_text.startswith("```json"):
                content_text = content_text[7:]
            if content_text.startswith("```"):
                content_text = content_text[3:]
            if content_text.endswith("```"):
                content_text = content_text[:-3]
            content_json = json.loads(content_text.strip())
            from core.sites_engine import enforce_title_60_70
            if isinstance(content_json, dict):
                if "page_title" in content_json:
                    content_json["page_title"] = enforce_title_60_70(content_json["page_title"], keyword)
                if "h1_title" in content_json:
                    content_json["h1_title"] = enforce_title_60_70(content_json["h1_title"], keyword)
            return content_json
        else:
            logger.error(f"AI API Error ({response.status_code}): {response.text}")
            return generate_fallback_content(keyword, structure)
    except Exception as e:
        logger.exception(f"Exception during AI content generation: {e}")
        return generate_fallback_content(keyword, structure)

def generate_fallback_content(keyword: str, structure: Any) -> Dict[str, Any]:
    """Generates a high-quality template when API is unreachable or unconfigured."""
    from core.sites_engine import enforce_title_60_70
    kw_title = keyword.strip().title()
    sections = []
    
    elements = getattr(structure, "elements", [])
    for el in elements:
        if getattr(el, "element_type", "") in ("h2_text", "content_block"):
            sections.append({
                "key": el.key,
                "h2_heading": f"Comprehensive {kw_title} Solutions & Guide",
                "body_text": f"Discover reliable and expert assistance regarding {keyword}. Our team ensures top-tier quality, transparent processes, and immediate support tailored specifically to meet modern standards. We focus on efficiency, reliability, and long-term customer satisfaction.",
                "image_caption": f"Professional overview of {keyword}"
            })

    if not sections:
        sections.append({
            "key": "main_content",
            "h2_heading": f"Comprehensive {kw_title} Solutions & Guide",
            "body_text": f"Discover reliable and expert assistance regarding {keyword}. Our team ensures top-tier quality, transparent processes, and immediate support tailored specifically to meet modern standards. We focus on efficiency, reliability, and long-term customer satisfaction.",
            "image_caption": f"Professional overview of {keyword}"
        })

    raw_title = f"{kw_title} - Official Portal & Verified Services"
    final_page_title = enforce_title_60_70(raw_title, keyword)

    return {
        "page_title": final_page_title,
        "header_tagline": f"Premier assistance and trusted expertise for {keyword}",
        "sections": sections,
        "map_query": "New Delhi, India",
        "footer_text": f"© 2026 {kw_title}. All rights reserved. Authorized informational resource."
    }
