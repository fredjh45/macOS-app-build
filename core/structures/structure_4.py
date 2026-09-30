"""
Structure 4: Authority Guide & Directory
Layout:
1. Hero Header Banner (Background Image from str-image4 + H1 Title 60-70 chars + Dual Docked CTA Buttons)
2. Executive Directory Overview & Verified Listings (H2 Headings + Multi-Paragraph Authority Guide Content)
3. 1 Full-Width Body Feature Image (from str-image4, distinct from hero)
4. 'Tag keywords –' Section & Bulk Keywords Box (60-80+ SEO keywords)
5. Google Maps Embed (Full Width, dynamic city/locality)
6. Publish site & return verified live URL
"""

import os
import re
import json
import time
import random
import logging
import requests
from typing import Dict, Any, List, Optional
from core.location_helper import extract_location_and_map_query, generate_comprehensive_tag_keywords

logger = logging.getLogger(__name__)

STRUCTURE_ID = "str-4"
STRUCTURE_NAME = "Structure 4: Authority Guide & Directory"
IMAGE_FOLDER_NAME = "str-image4"
DESCRIPTION = "Hero (str-image4 Bg + H1 + 2 Docked Buttons) -> Authority Directory Sections -> 1 Body Image -> 60-80 Tag Keywords -> Google Map Embed"


def generate_dynamic_structure_4_title(keyword: str, city: Optional[str] = None) -> str:
    """Generates dynamic 60-70 character SEO title for Structure 4: Authority Guide & Directory."""
    kw = keyword.strip().title()
    if not city:
        city, _ = extract_location_and_map_query(keyword)

    prefixes = [
        "Verified Guide:", "Top Rated", "Premier Directory:", "Elite Roster:",
        "Official Guide to", "The Complete Guide to", "Best Rated", "Direct VIP Desk:"
    ]
    suffixes = [
        f"in {city} | 24/7 Verified Booking Agency",
        f"in {city} | 100% Genuine Escort Directory",
        f"in {city} | Doorstep Service & Direct Rates",
        f"in {city} | Verified Independent Models Hub",
        f"in {city} | Immediate Cash On Delivery Desk",
        f"in {city} | VIP Companions & Direct Contact"
    ]

    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    raw_title = f"{prefix} {kw} {suffix}"

    from core.sites_engine import enforce_title_60_70
    return enforce_title_60_70(raw_title, kw)


def build_structure_4_prompt(keyword: str, related_keywords: Optional[List[str]] = None) -> str:
    """Builds the AI prompt for Structure 4 (Authority Guide & Directory)."""
    city, map_query = extract_location_and_map_query(keyword)
    if not related_keywords:
        kw_clean = keyword.strip()
        kw_list = [
            kw_clean, f"{kw_clean} Near Me", f"Best {kw_clean}", f"Affordable {kw_clean}",
            f"{kw_clean} in {city}", f"24/7 {kw_clean} {city}", f"Verified {kw_clean}",
            f"Doorstep {kw_clean}", f"Top Rated {kw_clean} Agency", f"Independent {kw_clean} {city}"
        ]
    else:
        kw_list = [k.strip() for k in related_keywords if k.strip()]

    kw_string = ", ".join(kw_list)

    prompt = f"""You are a master local SEO strategist and professional copywriter specializing in high-converting directory portals.
Generate complete structured text content for an authoritative local directory guide for keyword: '{keyword}' in '{city}'.

CRITICAL REQUIREMENTS:
1. Do NOT include any hyperlinks, URLs, phone numbers, or WhatsApp numbers in the text body paragraphs.
2. Target keywords to naturally incorporate: {kw_string}
3. Return pure, valid JSON only. Do not wrap with markdown code fences.
4. h1_title LENGTH RULE: 'h1_title' MUST be STRICTLY between 60 and 70 characters long (including spaces).
5. sections: Exactly 6 comprehensive sections, each having an engaging H2 heading and 2 informative, well-written paragraphs (100-140 words each paragraph).
6. bulk_keywords: 60 to 80 comma-separated related search queries, long-tail terms, and proximity phrases (~250-350 words total).
7. map_query: Specific city or locality for '{keyword}' (e.g. '{map_query}').

JSON Schema:
{{
    "h1_title": "Top Rated {keyword.title()} in {city} | 24/7 Verified Booking Agency",
    "sections": [
        {{
            "h2": "Comprehensive Overview & Verified Directory of {keyword.title()} in {city}",
            "paragraphs": ["Paragraph 1 (100-130 words)...", "Paragraph 2 (100-130 words)..."]
        }},
        {{
            "h2": "Unmatched Quality Standards and Client Safety Protocols in {city}",
            "paragraphs": ["Paragraph 1 (100-130 words)...", "Paragraph 2 (100-130 words)..."]
        }},
        {{
            "h2": "Transparent Pricing Packages and Instant Cash on Delivery Options",
            "paragraphs": ["Paragraph 1 (100-130 words)...", "Paragraph 2 (100-130 words)..."]
        }},
        {{
            "h2": "How Our Doorstep Dispatch and Rapid 20-Minute Arrival Operates",
            "paragraphs": ["Paragraph 1 (100-130 words)...", "Paragraph 2 (100-130 words)..."]
        }},
        {{
            "h2": "Exclusive VIP Profiles and Diverse Independent Categories in {city}",
            "paragraphs": ["Paragraph 1 (100-130 words)...", "Paragraph 2 (100-130 words)..."]
        }},
        {{
            "h2": "Direct WhatsApp Coordination and 24/7 Priority Helpline Assistance",
            "paragraphs": ["Paragraph 1 (100-130 words)...", "Paragraph 2 (100-130 words)..."]
        }}
    ],
    "bulk_keywords": "{keyword}, {keyword} Near Me, Best {keyword} in {city}, Verified {keyword}, Affordable {keyword}...",
    "map_query": "{map_query}"
}}
"""
    return prompt


def generate_structure_4_content(keyword: str, related_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generates AI content for Structure 4 using DeepSeek / Grok with robust fallback."""
    from database.db import get_setting
    provider = get_setting("active_ai_provider", "deepseek").lower()

    if "grok" in provider:
        api_key = get_setting("grok_api_key", "").strip()
        endpoint = "https://api.x.ai/v1/chat/completions"
        model = "grok-4.3"
    else:
        api_key = get_setting("deepseek_api_key", "").strip()
        endpoint = "https://api.deepseek.com/chat/completions"
        model = "deepseek-chat"

    if not api_key:
        logger.warning(f"[STR-4] No API key found for {provider}. Using fallback content.")
        return get_structure_4_fallback(keyword, related_keywords)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_structure_4_prompt(keyword, related_keywords)},
            {"role": "user", "content": f"Generate Structure 4 content for: '{keyword}' now."}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    if "grok" in provider:
        payload["reasoning_effort"] = "none"

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            content_str = r.json()["choices"][0]["message"]["content"].strip()
            if content_str.startswith("```json"):
                content_str = content_str[7:]
            if content_str.startswith("```"):
                content_str = content_str[3:]
            if content_str.endswith("```"):
                content_str = content_str[:-3]
            content_str = content_str.strip()
            first_brace = content_str.find("{")
            last_brace = content_str.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                content_str = content_str[first_brace:last_brace+1]
            parsed = json.loads(content_str)
            from core.sites_engine import enforce_title_60_70
            if isinstance(parsed, dict) and "h1_title" in parsed:
                parsed["h1_title"] = enforce_title_60_70(parsed["h1_title"], keyword)
            return parsed
        else:
            logger.error(f"[STR-4] API Error {r.status_code}: {r.text[:200]}")
            return get_structure_4_fallback(keyword, related_keywords)
    except Exception as e:
        logger.exception(f"[STR-4] Exception during AI generation: {e}")
        return get_structure_4_fallback(keyword, related_keywords)


def get_structure_4_fallback(keyword: str, related_keywords: Optional[List[str]] = None, city: Optional[str] = None) -> Dict[str, Any]:
    """Provides rich, localized fallback content for Structure 4: Authority Guide & Directory."""
    extracted_city, extracted_map = extract_location_and_map_query(keyword)
    actual_city = city or extracted_city
    kw_title = keyword.strip().title()
    h1 = generate_dynamic_structure_4_title(keyword, city=actual_city)

    sections = [
        {
            "h2": f"Comprehensive Overview & Verified Directory of {kw_title} in {actual_city}",
            "paragraphs": [
                f"Welcome to the premier authoritative local guide and verified directory for {keyword} in {actual_city}. Our directory is committed to bringing you meticulously verified, authentic, and premium companionship services designed for discerning individuals who value luxury, utmost discretion, and professional hospitality. Whether you are traveling for prestigious business meetings, enjoying a private luxury staycation, or seeking a charming social partner, our directory streamlines the selection process so you can discover top-tier profiles with complete confidence and peace of mind.",
                f"We recognize that finding trustworthy, genuine service providers in {actual_city} requires dependable information and transparent booking channels. That is why every listing on our directory features real photos, genuine details, and pre-screened etiquette. Our customer assistance coordinators are on hand 24 hours a day to guide you through available options, answer queries politely, and coordinate doorstep visits seamlessly without any hidden steps."
            ]
        },
        {
            "h2": f"Unmatched Quality Standards and Complete Client Privacy in {actual_city}",
            "paragraphs": [
                f"Client safety, confidentiality, and mutual respect represent the core foundations of our directory operations in {actual_city}. All independent companions featured within our network undergo thorough background checks and adhere to strict standards of personal hygiene, grooming, and polite conversational manners. We implement rigorous privacy protections, ensuring your phone number, personal identity, and booking choices remain strictly confidential at every stage.",
                f"Whether meeting at high-end luxury five-star hotels, premium boutique suites, or private residences, our companions arrive discreetly with zero fuss. Our quiet coordination ensures complete privacy from beginning to end, allowing you to relax and enjoy unmatched warmth, sophistication, and attentive company without any worries or complications."
            ]
        },
        {
            "h2": f"Transparent Pricing Packages and Direct Cash on Delivery Facility",
            "paragraphs": [
                f"We strictly advocate upfront, fair, and clear pricing with zero unexpected surcharges, advance deposits, or hidden booking fees. Our directory provides structured tariff plans suited to varying preferences, including brief refreshing appointments, leisurely dinner dates, corporate accompaniments, and relaxing overnight packages. Every quote shared by our customer desk is completely all-inclusive and final.",
                f"To ensure total trust, we offer 100% direct cash on delivery payment. You only pay after your companion arrives at your chosen venue and you are fully satisfied with the verified profile. This transparent policy eliminates financial risks and makes enjoying top-rated {keyword} in {actual_city} seamless, trustworthy, and stress-free."
            ]
        },
        {
            "h2": f"Rapid Doorstep Dispatch Operating Across All Key Areas of {actual_city}",
            "paragraphs": [
                f"Time is valuable, and our distributed network across {actual_city} enables rapid doorstep arrivals within 20 to 30 minutes of reservation confirmation. We maintain active associate coordinators stationed near prime commercial districts, hospitality hubs, transit points, and upscale residential sectors, ensuring rapid transit without annoying delays.",
                f"Simply send a brief message via WhatsApp or call our reservation desk directly to check real-time availability in your immediate locality. Our drivers and associates operate with quiet efficiency, guaranteeing on-time arrival directly at your hotel room or private premises so your plans proceed without a hitch."
            ]
        },
        {
            "h2": f"Exclusive Profiles and Diverse Premium Categories Available",
            "paragraphs": [
                f"Our directory showcases an impressive, versatile portfolio of independent models, college companions, air hostesses, corporate executives, and high-fashion models in {actual_city}. Each profile brings a unique blend of elegance, vibrant energy, and sophisticated charm tailored to your personal vibe and event requirements.",
                f"Explore verified photo galleries and select companions who match your exact criteria. Our friendly booking coordinators will confirm profile availability instantly, guaranteeing that the companion who arrives at your doorstep is the exact verified match you selected from our directory."
            ]
        },
        {
            "h2": f"Direct 24/7 WhatsApp Assistance and Simple Booking Steps",
            "paragraphs": [
                f"Reserving your chosen companion is fast and straightforward. With direct WhatsApp connectivity and round-the-clock priority calling lines, you can complete your reservation in under two minutes without lengthy forms or confusing procedures.",
                f"Contact our team today via the buttons above or direct WhatsApp to experience unmatched elegance, delightful company, and premier hospitality with the most trusted {keyword} service directory in {actual_city}."
            ]
        }
    ]

    bulk_kw = generate_comprehensive_tag_keywords(keyword, actual_city, related_keywords)
    if isinstance(bulk_kw, list):
        bulk_kw = ", ".join(bulk_kw)

    return {
        "h1_title": h1,
        "sections": sections,
        "bulk_keywords": bulk_kw,
        "map_query": extracted_map
    }


def execute_structure_4(
    automator,
    keyword: str,
    phone_number: str,
    whatsapp_link: str,
    ai_content: Optional[Dict[str, Any]] = None,
    related_keywords: Optional[List[str]] = None,
    theme_name: str = "Simple",
    theme_color_hex: Optional[str] = None,
    enable_announcement: bool = False,
    announcement_message: Optional[str] = None,
    banner_color: Optional[str] = "#FF0000",
    use_demo_content: bool = False,
    image_folder_override: Optional[str] = None
) -> Optional[str]:
    """
    Executes Structure 4: Authority Guide & Directory workflow on Google Sites.
    Layout:
    1. Hero Header Banner (Background Image from str-image4 + H1 Title 60-70 chars + Dual Docked CTA Buttons)
    2. 6 Authority Guide Sections (H2 Headings + Multi-Paragraph Authority Guide Content)
    3. 1 Full-Width Feature Body Image (from str-image4, distinct from hero)
    4. 'Tag keywords –' Section & Bulk Keywords Box (60-80+ SEO keywords)
    5. Google Maps Embed (Full Width, dynamic city/locality)
    6. Publish site & return verified live URL
    """
    automator.log("[STR-4] Starting Execution for Structure 4: Authority Guide & Directory...")

    city_detected, map_detected = extract_location_and_map_query(keyword)

    # 1. Prepare Content
    if not ai_content:
        if use_demo_content:
            automator.log(f"[STR-4] Using instant fallback content for: '{keyword}'...")
            ai_content = get_structure_4_fallback(keyword, related_keywords, city=city_detected)
        else:
            automator.log(f"[STR-4] Generating AI content for: '{keyword}'...")
            ai_content = generate_structure_4_content(keyword, related_keywords)

    from core.sites_engine import enforce_title_60_70
    h1_title = enforce_title_60_70(ai_content.get("h1_title") or generate_dynamic_structure_4_title(keyword, city=city_detected), keyword)
    site_name = h1_title
    sections = ai_content.get("sections", [])

    # Ensure robust, abundant Tag Keywords (60-80+)
    bulk_keywords_text = ai_content.get("bulk_keywords")
    if not bulk_keywords_text or len([k for k in bulk_keywords_text.split(",") if k.strip()]) < 30:
        bulk_keywords_res = generate_comprehensive_tag_keywords(keyword, city_detected, related_keywords)
        bulk_keywords_text = ", ".join(bulk_keywords_res) if isinstance(bulk_keywords_res, list) else bulk_keywords_res

    # Ensure Map Query reflects the actual location
    map_query = ai_content.get("map_query")
    if not map_query or ("dehradun" in map_query.lower() and "dehradun" not in keyword.lower()):
        map_query = map_detected

    # Phone link & WhatsApp link preparation
    if phone_number:
        clean_phone = re.sub(r'[^0-9+]', '', phone_number)
        tel_url = f"tel:{clean_phone}"
    else:
        tel_url = "tel:+919876543210"

    if whatsapp_link:
        wa_clean = whatsapp_link.strip()
        if not wa_clean.startswith("http"):
            wa_num = re.sub(r'[^0-9]', '', wa_clean)
            wa_clean = f"https://wa.me/{wa_num}"
    else:
        wa_clean = "https://wa.me/919876543210"

    # ==========================================
    # PRE-EXECUTION: Blank Site, Theme & Announcement
    # ==========================================
    if not automator.create_blank_site():
        automator.log("[STR-4] [ERROR] Failed to create blank site.")
        return None

    # Apply Site Theme
    target_theme = theme_name or "Simple"
    automator.select_google_theme(target_theme)

    # Apply Announcement Banner if enabled
    if enable_announcement:
        banner_msg = announcement_message or f"24/7 Verified Service for {keyword.title()} - Contact Now"
        automator.set_announcement_banner(
            message=banner_msg,
            button_label="Call Now",
            link=tel_url
        )

    # ==========================================
    # BLOCK 1: Hero Section (Header Background Image from str-image4 + H1 Title + Dual Docked Buttons)
    # ==========================================
    target_img_folder = image_folder_override or IMAGE_FOLDER_NAME
    images = automator.upload_structure_images(target_img_folder)
    if images:
        random.shuffle(images)
    if len(images) > 0:
        hero_img_path = images[0]
        automator.log(f"[STR-4] [HERO] Randomly picked Hero background image from {target_img_folder}: {os.path.basename(hero_img_path)}")
        automator.set_header_background_image(hero_img_path)

    automator.log(f"[STR-4] [HERO] Setting Site Name & Header Title to: '{h1_title}'...")
    automator.set_document_name(site_name)
    automator.set_header_title(h1_title)

    # Insert Button 1: 'Call Now' docked into Header
    automator.log("[STR-4] [HERO] Docking Button 1 ('Call Now') under Header Title...")
    automator.add_button_element("Call Now", tel_url, drag_to_header=True)

    # Insert Button 2: 'WhatsApp Now' docked into Header
    automator.log("[STR-4] [HERO] Docking Button 2 ('WhatsApp Now') under Header Title...")
    automator.add_button_element("WhatsApp Now", wa_clean, drag_to_header=True)

    # ==========================================
    # BLOCKS 2 to 7: Authority Guide Sections
    # ==========================================
    for idx, sec in enumerate(sections):
        sec_num = idx + 1
        automator.log(f"[STR-4] [SECTION {sec_num}/{len(sections)}] Adding H2 Heading: '{sec['h2'][:40]}...'")
        automator.add_h2_heading_section(sec["h2"])

        paras = sec.get("paragraphs", [])
        if paras:
            automator.log(f"[STR-4] [SECTION {sec_num}/{len(sections)}] Adding Normal Text ({len(paras)} paras)...")
            automator.add_normal_text_box(paras)

    # ==========================================
    # BLOCK 8: 1 Full-Width Body Feature Image (from str-image4, distinct from hero)
    # ==========================================
    if len(images) > 1:
        body_img = images[1]
    elif len(images) > 0:
        body_img = images[0]
    else:
        body_img = None

    if body_img and os.path.exists(body_img):
        automator.log(f"[STR-4] [IMAGE] Adding 1 Full-Width Body Image from {target_img_folder}: {os.path.basename(body_img)}...")
        automator.add_image_element(body_img, make_full_width=True)
        try:
            automator.page.wait_for_timeout(800)
            img_sec = automator.page.locator("article section").last
            if img_sec.count() > 0:
                img_sec.scroll_into_view_if_needed()
                automator.page.wait_for_timeout(400)
                box = img_sec.bounding_box()
                if box and box['height'] > 20:
                    cx = box['x'] + box['width'] / 2
                    cy = box['y'] + box['height'] / 2
                    automator.page.mouse.click(cx, cy)
                    automator.page.wait_for_timeout(500)
                    automator.log(f"[STR-4] Clicked feature image at ({cx:.1f}, {cy:.1f}) to anchor subsequent Tag keywords strictly below it.")
                else:
                    automator.page.mouse.click(500, 700)
                    automator.page.wait_for_timeout(500)
        except Exception as e:
            automator.log(f"[STR-4] Notice anchoring to feature image: {e}")

    # ==========================================
    # BLOCK 9: Tag Keywords Section & Bulk Keywords Box (60-80+ SEO keywords)
    # ==========================================
    automator.log("[STR-4] [TAGS] Adding 'Tag keywords –' Section & Bulk Keywords Box...")
    automator.add_h2_heading_section("Tag keywords –")
    automator.add_bulk_keywords_box(bulk_keywords_text)

    # ==========================================
    # BLOCK 10: Google Maps Embed (Full Width)
    # ==========================================
    automator.log(f"[STR-4] [MAP] Embedding Google Map for: '{map_query}'...")
    automator.add_map_embed(map_query, make_full_width=True)

    # ==========================================
    # BLOCK 11: Publishing & Live URL Extraction
    # ==========================================
    automator.log("[STR-4] All sections added successfully. Proceeding to Publish...")
    pub_url = automator.publish_and_get_url(keyword)

    from database.db import add_task_history
    add_task_history(
        keyword=keyword,
        structure_used=STRUCTURE_NAME,
        phone_number=phone_number,
        whatsapp_link=whatsapp_link,
        published_url=pub_url or "",
        status="SUCCESS" if pub_url else "FAILED"
    )
    return pub_url

# Backward/dynamic compatibility alias
execute_str_4 = execute_structure_4
