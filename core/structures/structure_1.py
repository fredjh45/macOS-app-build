"""
Structure 1: 35-Block High-Authority SEO Page Definition
Layout:
1. Hero Section (Full Width):
   - Background Image (from images/str-image1/)
   - H1: Custom AI-generated Title (Used as Site Name as per user rule)
   - Button: 'WHATSAPP' (wa.me/...) docked directly under H1 in header
2. Text Box – H2 Heading with Background Theme Color Section (Style 3)
3. Text Box – Normal Text (2 AI paragraphs, ~150 words)
4. Button – Full Width: 'Call Now' (tel:+...)
5. Text Box – H2 Heading with Background Theme Color Section (Style 3)
6. Image Upload + Normal Text (Option B: Stacked Image + 2 AI paragraphs)
7. Text Box – H2 Heading with Background Theme Color Section (Style 3)
8. Text Box – Normal Text (3 AI paragraphs)
9. Text Box – H2 Heading with Background Theme Color Section (Style 3)
10. Image Upload + Normal Text (Stacked Image + 3 AI paragraphs)
11. Text Box – H2 Heading with Background Theme Color Section (Style 3)
12. Text Box – Normal Text (4 AI paragraphs)
13. Text Box – H2 Heading with Background Theme Color Section (Style 3)
14. Image Upload + Normal Text (Stacked Image + 3 AI paragraphs)
15. Text Box – H2 Heading with Background Theme Color Section (Style 3)
16. Text Box – Normal Text (3 AI paragraphs)
17. Text Box – H2 Heading with Background Theme Color Section (Style 3)
18. Image Upload + Normal Text (Stacked Image + 3 AI paragraphs)
19. Text Box – H2 Heading with Background Theme Color Section (Style 3)
20. Text Box – Normal Text (3 AI paragraphs)
21. Text Box – H2 Heading with Background Theme Color Section (Style 3)
22. Image Upload + Normal Text (Stacked Image + 4 AI paragraphs)
23. Text Box – H2 Heading with Background Theme Color Section (Style 3)
24. Text Box – Normal Text (3 AI paragraphs)
25. Text Box – H2 Heading with Background Theme Color Section (Style 3)
26. Image Upload + Normal Text (Stacked Image + 3 AI paragraphs)
27. Text Box – H2 Heading with Background Theme Color Section (Style 3)
28. Text Box – Normal Text (3 AI paragraphs)
29. Text Box – H2 Heading with Background Theme Color Section (Style 3)
30. Image Upload + Normal Text (Stacked Image + 3 AI paragraphs)
31. Text Box – H2 Heading with Background Theme Color Section (Style 3)
32. Text Box – Normal Text (4 AI paragraphs)
33. Button – Full Width: 'Call Now' (tel:+...)
34. Text Box – Bulk Keywords
35. Map: Google Maps Embed (Custom location)
"""

import os
import re
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional
logger = logging.getLogger(__name__)

STRUCTURE_ID = "str-1"
STRUCTURE_NAME = "Structure 1: 35-Block High-Authority SEO Page"
IMAGE_FOLDER_NAME = "str-image1"
DESCRIPTION = "Hero (Bg Image + H1 + WhatsApp Button) -> 15 Theme Color H2 Headings -> Normal Text Paragraphs -> 7 Uploaded Images -> 2 Full-Width Call Buttons -> Bulk Keywords -> Google Maps"


import random
from core.location_helper import extract_location_and_map_query, generate_comprehensive_tag_keywords

def generate_dynamic_structure_1_title(keyword: str, city: Optional[str] = None) -> str:
    """Generates dynamic multi-segment H1 title matching Image 3 (Pooja Agarwal – Delhi's Most Desired Escort – Your Ultimate Night Partner)."""
    kw = keyword.strip().title()
    if not city:
        city, _ = extract_location_and_map_query(keyword)
    names = [
        "Pooja Agarwal", "Riya Kapoor", "Sneha Sharma", "Ananya Sen",
        "Simran Roy", "Kavya Malhotra", "Tanya Verma", "Neha Joshi",
        "Priya Singhania", "Muskan Khan", "Shreya Rajput", "Mehak Oberoi"
    ]
    superlatives = [
        "Most Desired", "Top Rated VIP", "Premier Choice",
        "Most Trusted", "Exclusive & Elite", "Number #1 Rated",
        "Highly Acclaimed", "Super High Class"
    ]
    taglines = [
        "Your Ultimate Night Partner", "100% Genuine & Discreet Companions",
        "24/7 Luxury Doorstep Experience", "Pure Elegance & Unmatched Comfort",
        "Direct Cash Booking & Fast Arrival", "Verified Five Star Service",
        "Passionate Connections & Absolute Privacy", "Unforgettable Moments & VIP Treatment"
    ]
    name = random.choice(names)
    sup = random.choice(superlatives)
    tag = random.choice(taglines)
    raw_title = f"{name} – {city}'s {sup} {kw} – {tag}"
    from core.sites_engine import enforce_title_60_70
    return enforce_title_60_70(raw_title, kw)


def build_structure_1_prompt(keyword: str, related_keywords: Optional[List[str]] = None) -> str:
    """Builds the specialized AI prompt for Structure 1 (15 H2 sections with strictly 2 paras each + Bulk Keywords)."""
    city, map_query = extract_location_and_map_query(keyword)
    if not related_keywords:
        kw_clean = keyword.strip()
        kw_list = [
            kw_clean, f"{kw_clean} Near Me", f"Best {kw_clean}", f"Affordable {kw_clean}",
            f"{kw_clean} Services", f"Emergency {kw_clean}", f"24/7 {kw_clean}",
            f"{kw_clean} Price", f"{kw_clean} Fast Service", f"Top Rated {kw_clean}",
            f"{kw_clean} Agency", f"Verified {kw_clean}", f"Doorstep {kw_clean}",
            f"{kw_clean} in {city}", f"Best {kw_clean} {city}", f"Local {kw_clean} {city}"
        ]
    else:
        kw_list = [k.strip() for k in related_keywords if k.strip()]

    kw_string = ", ".join(kw_list)

    prompt = f"""You are an elite SEO content writer for a Google Sites high-authority local webpage.
Your task is to generate complete structured text content following the EXACT 15-section specifications below for keyword: '{keyword}'.

CRITICAL RULES:
1. Do NOT include hyperlinks, URLs, phone numbers, or WhatsApp numbers inside the text body.
2. Target keywords: {kw_string}
   Integrate them naturally across headings and paragraphs.
3. Return pure, valid JSON only. Do not wrap with markdown blocks or backticks.
4. Keep each paragraph punchy, engaging, and professional (around 45-60 words each). Every single section MUST have STRICTLY 2 PARAGRAPHS.
5. h1_title LENGTH RULE: 'h1_title' MUST be STRICTLY between 60 and 70 characters long (including spaces). Never make it shorter than 60 or longer than 70 characters.

Structure Requirements:
1. h1_title: An eye-catching, multi-segment H1 title strictly 60 to 70 characters formatted with en-dashes ( – ).
    Format: '[Featured Name] – {city}\'s [Superlative] [Keyword] – [Short Tagline]' (Strictly 60-70 characters total)
    Reference Example: 'Pooja Agarwal – {city} Top VIP – 24/7 Verified Service'

2. sections: Exactly 15 H2 sections with STRICTLY 2 PARAGRAPHS EACH (45-60 words per paragraph):
   - Section 1: H2 Heading + 2 paragraphs (Service overview & warm welcome)
   - Section 2: H2 Heading + 2 paragraphs (Why choose verified professional assistance)
   - Section 3: H2 Heading + 2 paragraphs (Top notch quality & verified standards)
   - Section 4: H2 Heading + 2 paragraphs (Local area booking & quick reach)
   - Section 5: H2 Heading + 2 paragraphs (Affordable price packages & value deals)
   - Section 6: H2 Heading + 2 paragraphs (24/7 direct helpline & fast support)
   - Section 7: H2 Heading + 2 paragraphs (Exclusive features & customer satisfaction)
   - Section 8: H2 Heading + 2 paragraphs (Unmatched expertise, privacy & discretion)
   - Section 9: H2 Heading + 2 paragraphs (Wide variety & verified profiles in city)
   - Section 10: H2 Heading + 2 paragraphs (Immediate booking confirmation)
   - Section 11: H2 Heading + 2 paragraphs (Safe & reliable service standard guarantee)
   - Section 12: H2 Heading + 2 paragraphs (Experience pure comfort, luxury & convenience)
   - Section 13: H2 Heading + 2 paragraphs (Easy booking steps & transparent terms)
   - Section 14: H2 Heading + 2 paragraphs (Direct doorstep availability anytime)
   - Section 15: H2 Heading + 2 paragraphs (About our agency & commitment to excellence)

3. bulk_keywords: 60-80 comma-separated related search queries and tags (~200-300 words).
4. map_query: Specific city or locality for '{keyword}' (e.g. '{map_query}').

The JSON output MUST follow this exact schema:
{{
    "h1_title": "Pooja Agarwal – {city}'s Most Desired Service – Your Ultimate Night Partner",
    "sections": [
        {{"h2": "Get A Complete Overview Of Our High Class Service", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Why Choose Professional Assistance Over Traditional", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Top Notch Quality Guarantee With Verified Experts", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Book The Perfect Match Directly Near Your Location", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Affordable Price Packages Tailored For Complete Satisfaction", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "24/7 Available Direct Helpline And Fast Support", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Exclusive Features And Customer Satisfaction", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Unmatched Expertise And Discretion In Every Booking", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Explore Wide Variety And Verified Profiles In Your City", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Immediate Booking Confirmation Via WhatsApp Or Direct Call", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Safe & Reliable Service Standard Guarantee", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Experience Pure Luxury And Comfort Near You", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Easy Booking Steps And Payment Options", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "Direct Assistance Available Anytime Near You", "paragraphs": ["Para 1...", "Para 2..."]}},
        {{"h2": "About Our Agency & Commitment To Excellence", "paragraphs": ["Para 1...", "Para 2..."]}}
    ],
    "bulk_keywords": "{keyword}, {keyword} Near Me, Best {keyword} in {city}, Affordable {keyword} in {city}, 24/7 {keyword}...",
    "map_query": "{map_query}"
}}
"""
    return prompt


def generate_structure_1_content(keyword: str, related_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generates AI content for Structure 1 using DeepSeek / Grok, with robust fallback."""
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
        logger.warning(f"[STR-1] No API key found for {provider}. Using Structure 1 fallback.")
        return get_structure_1_fallback(keyword, related_keywords)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_structure_1_prompt(keyword, related_keywords)},
            {"role": "user", "content": f"Generate Structure 1 content for keyword: '{keyword}' now."}
        ],
        "temperature": 0.75,
        "max_tokens": 8000
    }
    if "grok" in provider:
        payload["reasoning_effort"] = "none"

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=75)
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
            return parsed
        else:
            logger.error(f"[STR-1] API Error {r.status_code}: {r.text[:200]}")
            return get_structure_1_fallback(keyword, related_keywords)
    except Exception as e:
        logger.exception(f"[STR-1] Exception during AI generation: {e}")
        return get_structure_1_fallback(keyword, related_keywords)


def get_structure_1_fallback(keyword: str, related_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """High-quality 15-section fallback adhering strictly to Structure 1 (strictly 2 paras per section)."""
    city, map_query = extract_location_and_map_query(keyword)
    kw_title = keyword.strip().title()
    h1 = generate_dynamic_structure_1_title(keyword, city=city)

    sections = [
        {
            "h2": f"Get A Complete Overview Of Our High Class {kw_title}",
            "paragraphs": [
                f"Welcome to the premier destination for trusted and verified {keyword}. We provide an outstanding experience designed to exceed your highest expectations with absolute discretion and unmatched professionalism.",
                f"Our specialized services bring together elite standards and verified excellence, ensuring a seamless and thoroughly satisfying interaction from beginning to end."
            ]
        },
        {
            "h2": f"Why Choose Professional Assistance Over Traditional {kw_title}",
            "paragraphs": [
                f"Opting for verified professionals ensures absolute peace of mind and top-tier reliability for {keyword}. We eliminate uncertainties by offering only genuine, vetted profiles and transparent solutions.",
                f"Every booking is handled with meticulous attention to privacy, ensuring complete confidentiality and a personalized touch tailored to your preferences."
            ]
        },
        {
            "h2": f"Top Notch Quality Guarantee With Verified Experts in {city}",
            "paragraphs": [
                f"Quality and authenticity are the foundation of our reputation. Each associate on our roster undergoes thorough screening and professional etiquette verification.",
                f"We maintain stringent service benchmarks so you receive only five-star companionship and attentive care on every single appointment."
            ]
        },
        {
            "h2": f"Book The Perfect Match Directly Near Your Location in {city}",
            "paragraphs": [
                f"Finding your ideal companion in {city} has never been more effortless, transparent, or dependable. We maintain comprehensive network coverage across all premier districts and luxury hotels.",
                f"Whether you are situated near the city center or in quiet residential neighborhoods, our associates arrive punctually with courteous elegance and quiet discretion."
            ]
        },
        {
            "h2": f"Affordable Price Packages Tailored For Complete Satisfaction",
            "paragraphs": [
                f"We believe elite companionship should offer outstanding value alongside transparent pricing. Our clear tariff structures feature zero hidden extras or surprise charges.",
                f"From romantic dinner dates to full-evening engagements, each package is thoughtfully customized to match your budget and exact expectations."
            ]
        },
        {
            "h2": f"24/7 Available Direct Helpline And Fast Support in {city}",
            "paragraphs": [
                f"Connecting with our reservations team is instantaneous and available round the clock through our priority WhatsApp desk and dedicated telephone lines.",
                f"Our courteous coordinators respect your schedule, answering your inquiries swiftly and confirming your appointments without cumbersome delays or paperwork."
            ]
        },
        {
            "h2": f"Exclusive Features And Customer Satisfaction in {city}",
            "paragraphs": [
                f"Every encounter is treated as a unique VIP experience designed exclusively around your comfort, personal preferences, and individual boundaries.",
                f"We continuously upgrade our hospitality standards to deliver delightful, refreshing, and deeply rewarding private leisure moments."
            ]
        },
        {
            "h2": f"Unmatched Expertise And Discretion In Every Booking",
            "paragraphs": [
                f"Privacy is paramount for our valued clientele. We implement strict non-disclosure policies to ensure your personal details remain 100% confidential at all times.",
                f"Relax in complete security knowing that your personal schedule and identity are safeguarded by seasoned industry professionals."
            ]
        },
        {
            "h2": f"Explore Wide Variety And Verified Profiles in {city}",
            "paragraphs": [
                f"Discover a magnificent roster of independent companions, from charming college models to sophisticated corporate hostesses and VIP international models.",
                f"Each profile is displayed with genuine verified photographs, allowing you to choose with absolute certainty and complete peace of mind."
            ]
        },
        {
            "h2": f"Immediate Booking Confirmation Via WhatsApp Or Direct Call",
            "paragraphs": [
                f"Experience seamless on-demand coordination with immediate booking acknowledgments. Simply drop a message or place a brief call to our team.",
                f"We promptly share available options and confirm your preferred time slot within minutes, ensuring zero awkward delays or stress."
            ]
        },
        {
            "h2": f"Safe & Reliable Service Standard Guarantee Across {city}",
            "paragraphs": [
                f"Safety, hygiene, and mutual respect form the cornerstone of every single engagement arranged through our platform.",
                f"We adhere strictly to highest standards of cleanliness and health protocols, providing a worry-free private environment where you can truly unwind."
            ]
        },
        {
            "h2": f"Experience Pure Luxury And Comfort Near You",
            "paragraphs": [
                f"Transform your solitary evenings into unforgettable memories enriched with genuine warmth, refined conversational charm, and attentive hospitality.",
                f"Our companions possess natural grace and polite manners, making them wonderful company for upscale gatherings as well as private hotel retreats."
            ]
        },
        {
            "h2": f"Easy Booking Steps And Direct Cash Payment Options",
            "paragraphs": [
                f"We provide straightforward 100% direct cash on delivery payment options, eliminating financial ambiguities or upfront deposit stress.",
                f"Pay securely after your companion arrives and you are thoroughly delighted with your booking arrangements and warm hospitality."
            ]
        },
        {
            "h2": f"Direct Assistance Available Anytime Near You in {city}",
            "paragraphs": [
                f"No matter what hour you desire attentive company, our 24-hour service associates are ready for prompt dispatch to your luxury suite or private quarters.",
                f"Enjoy rapid 20-30 minute doorstep arrivals that blend seamlessly into any hotel or residential lobby without drawing unwanted attention."
            ]
        },
        {
            "h2": f"About Our Agency & Commitment To Excellence",
            "paragraphs": [
                f"With years of dedicated experience and thousands of delighted patrons, our agency remains the gold standard for premier companionship in the region.",
                f"Contact our team today via WhatsApp or phone call to discover why hundreds of satisfied patrons choose us time and time again."
            ]
        }
    ]

    bulk_kw = generate_comprehensive_tag_keywords(keyword, city, related_keywords)

    return {
        "h1_title": h1,
        "sections": sections,
        "bulk_keywords": bulk_kw,
        "map_query": map_query
    }


def execute_structure_1(
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
    Executes the exact 35-Block Structure 1 workflow on Google Sites.
    Option B is applied for Image + Text blocks (Stacked Full-Width Image + Normal Text Box).
    User rule: The Hero Section H1 title is used directly as the site name!
    use_demo_content: When True (default for testing), uses instant local demo content without waiting for AI API calls.
    """
    automator.log("[STR-1] Starting 35-Block Execution for Structure 1...")

    # Dynamic location extraction
    city, default_map = extract_location_and_map_query(keyword)

    # 1. Prepare Content
    if not ai_content:
        if use_demo_content:
            automator.log(f"[STR-1] Using Instant Fallback Content: '{keyword}' (City: {city})...")
            ai_content = get_structure_1_fallback(keyword, related_keywords)
        else:
            automator.log(f"[STR-1] Generating AI content for: '{keyword}' (City: {city})...")
            ai_content = generate_structure_1_content(keyword, related_keywords)

    h1_title = ai_content.get("h1_title") or generate_dynamic_structure_1_title(keyword, city=city)
    # RULE: hero section title is used as site name
    site_name = h1_title
    sections = ai_content.get("sections", [])
    
    # Ensure abundant 60-80+ SEO tag keywords
    bulk_keywords_text = ai_content.get("bulk_keywords") or ""
    if not bulk_keywords_text or len(bulk_keywords_text.split(",")) < 30:
        bulk_keywords_text = generate_comprehensive_tag_keywords(keyword, city, related_keywords)

    map_query = ai_content.get("map_query") or default_map
    if "dehradun" in map_query.lower() and "dehradun" not in keyword.lower():
        map_query = default_map

    page = automator.page

    # Phone link preparation for Call Now buttons and banner
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
        automator.log("[STR-1] [ERROR] Failed to create blank site.")
        return None

    # Apply Site Theme
    if theme_name and theme_name.strip().lower() != "simple":
        automator.select_google_theme(theme_name)

    # Apply Announcement Banner if enabled
    if enable_announcement:
        banner_msg = announcement_message or f"24/7 Support Available for {keyword.title()} - Call Now"
        automator.set_announcement_banner(
            message=banner_msg,
            button_label="Call Now",
            link=tel_url
        )

    # ==========================================
    # BLOCK 1: Hero Section (Full Width Bg Image + H1 Title + WhatsApp Button)
    # ==========================================
    # 1. Upload Hero Background Image FIRST (ensures clean compact banner state)
    target_folder = image_folder_override or IMAGE_FOLDER_NAME
    images = automator.upload_structure_images(target_folder)
    if images:
        random.shuffle(images)
    num_images = len(images)
    if num_images > 0:
        hero_img_path = images[0]
        automator.log(f"[STR-1] Randomly selected unique Hero background image: {os.path.basename(hero_img_path)}")
        automator.set_header_background_image(hero_img_path)

    # 2. Setting Site Name & Header Title
    automator.log(f"[STR-1] [HERO] Setting Site Name & Header Title to: '{h1_title}'...")
    automator.set_document_name(site_name)
    automator.set_header_title(h1_title)

    # 3. Insert Hero Button: "WHATSAPP" docked right under H1 title in header
    automator.log("[STR-1] [BLOCK 1] Docking 'WHATSAPP' button under H1 title in Hero header...")
    automator.add_button_element("WHATSAPP", wa_clean, drag_to_header=True)

    img_counter = 0

    def get_next_image() -> Optional[str]:
        nonlocal img_counter
        if num_images == 0:
            return None
        # Start using images from index 1 (index 0 was hero). If folder has >= 8 images, each body image is 100% unique and never repeats!
        img = images[(img_counter + 1) % num_images] if num_images > 1 else images[0]
        img_counter += 1
        automator.log(f"[STR-1] Randomly selected unique body image #{img_counter}: {os.path.basename(img)}")
        return img

    def get_sec(idx: int) -> Dict[str, Any]:
        if idx < len(sections):
            return sections[idx]
        return {
            "h2": f"Essential Information & Professional Insights Part {idx+1}",
            "paragraphs": [
                f"High-quality, certified assistance for {keyword}.",
                f"Safe, prompt, and dependable execution delivered by industry specialists."
            ]
        }

    # ==========================================
    # BLOCK 2: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 2] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(0)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 3: Text Box – Normal Text (2 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 3] Adding Normal Text Box (2 paragraphs)...")
    automator.add_normal_text_box(get_sec(0)["paragraphs"][:2])

    # ==========================================
    # BLOCK 4: Button – Full Width ('Call Now')
    # ==========================================
    automator.log("[STR-1] [BLOCK 4] Adding Full-Width 'Call Now' Button...")
    automator.add_button_element("Call Now", tel_url, make_full_width=True)

    # ==========================================
    # BLOCK 5: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 5] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(1)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 6: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 6] Adding Image Upload + Normal Text (2 paragraphs)...")
    img6 = get_next_image()
    if img6 and os.path.exists(img6):
        automator.add_image_element(img6, make_full_width=True)
    automator.add_normal_text_box(get_sec(1)["paragraphs"][:2])

    # ==========================================
    # BLOCK 7: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 7] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(2)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 8: Text Box – Normal Text (3 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 8] Adding Normal Text Box (3 paragraphs)...")
    automator.add_normal_text_box(get_sec(2)["paragraphs"][:3])

    # ==========================================
    # BLOCK 9: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 9] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(3)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 10: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 10] Adding Image Upload + Normal Text (3 paragraphs)...")
    img10 = get_next_image()
    if img10 and os.path.exists(img10):
        automator.add_image_element(img10, make_full_width=True)
    automator.add_normal_text_box(get_sec(3)["paragraphs"][:3])

    # ==========================================
    # BLOCK 11: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 11] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(4)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 12: Text Box – Normal Text (4 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 12] Adding Normal Text Box (4 paragraphs)...")
    automator.add_normal_text_box(get_sec(4)["paragraphs"][:4])

    # ==========================================
    # BLOCK 13: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 13] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(5)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 14: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 14] Adding Image Upload + Normal Text (3 paragraphs)...")
    img14 = get_next_image()
    if img14 and os.path.exists(img14):
        automator.add_image_element(img14, make_full_width=True)
    automator.add_normal_text_box(get_sec(5)["paragraphs"][:3])

    # ==========================================
    # BLOCK 15: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 15] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(6)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 16: Text Box – Normal Text (3 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 16] Adding Normal Text Box (3 paragraphs)...")
    automator.add_normal_text_box(get_sec(6)["paragraphs"][:3])

    # ==========================================
    # BLOCK 17: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 17] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(7)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 18: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 18] Adding Image Upload + Normal Text (3 paragraphs)...")
    img18 = get_next_image()
    if img18 and os.path.exists(img18):
        automator.add_image_element(img18, make_full_width=True)
    automator.add_normal_text_box(get_sec(7)["paragraphs"][:3])

    # ==========================================
    # BLOCK 19: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 19] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(8)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 20: Text Box – Normal Text (3 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 20] Adding Normal Text Box (3 paragraphs)...")
    automator.add_normal_text_box(get_sec(8)["paragraphs"][:3])

    # ==========================================
    # BLOCK 21: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 21] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(9)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 22: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 22] Adding Image Upload + Normal Text (4 paragraphs)...")
    img22 = get_next_image()
    if img22 and os.path.exists(img22):
        automator.add_image_element(img22, make_full_width=True)
    automator.add_normal_text_box(get_sec(9)["paragraphs"][:4])

    # ==========================================
    # BLOCK 23: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 23] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(10)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 24: Text Box – Normal Text (3 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 24] Adding Normal Text Box (3 paragraphs)...")
    automator.add_normal_text_box(get_sec(10)["paragraphs"][:3])

    # ==========================================
    # BLOCK 25: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 25] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(11)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 26: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 26] Adding Image Upload + Normal Text (3 paragraphs)...")
    img26 = get_next_image()
    if img26 and os.path.exists(img26):
        automator.add_image_element(img26, make_full_width=True)
    automator.add_normal_text_box(get_sec(11)["paragraphs"][:3])

    # ==========================================
    # BLOCK 27: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 27] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(12)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 28: Text Box – Normal Text (3 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 28] Adding Normal Text Box (3 paragraphs)...")
    automator.add_normal_text_box(get_sec(12)["paragraphs"][:3])

    # ==========================================
    # BLOCK 29: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 29] Adding H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(13)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 30: Image Upload + Normal Text (Option B: Stacked)
    # ==========================================
    automator.log("[STR-1] [BLOCK 30] Adding Image Upload + Normal Text (3 paragraphs)...")
    img30 = get_next_image()
    if img30 and os.path.exists(img30):
        automator.add_image_element(img30, make_full_width=True)
    automator.add_normal_text_box(get_sec(13)["paragraphs"][:3])

    # ==========================================
    # BLOCK 31: Text Box – H2 Heading (Theme Color Style 3)
    # ==========================================
    automator.log("[STR-1] [BLOCK 31] Adding Final H2 Heading (Theme Color)...")
    automator.add_h2_heading_section(get_sec(14)["h2"], section_style="Style 3")

    # ==========================================
    # BLOCK 32: Text Box – Normal Text (4 paragraphs)
    # ==========================================
    automator.log("[STR-1] [BLOCK 32] Adding Final Normal Text Box (4 paragraphs)...")
    automator.add_normal_text_box(get_sec(14)["paragraphs"][:4])

    # ==========================================
    # BLOCK 33: Button – Full Width ('Call Now')
    # ==========================================
    automator.log("[STR-1] [BLOCK 33] Adding Bottom Full-Width 'Call Now' Button...")
    automator.add_button_element("Call Now", tel_url, make_full_width=True)

    # ==========================================
    # BLOCK 34: Text Box – Bulk Keywords
    # ==========================================
    automator.log("[STR-1] [BLOCK 34] Adding Bulk Keywords Box...")
    automator.add_bulk_keywords_box(bulk_keywords_text)

    # ==========================================
    # BLOCK 35: Map: Google Maps Embed (Full Width)
    # ==========================================
    automator.log(f"[STR-1] [BLOCK 35] Embedding Google Map for: '{map_query}'...")
    automator.add_map_embed(map_query, make_full_width=True)

    # ==========================================
    # PUBLISHING & LIVE URL EXTRACTION
    # ==========================================
    automator.log("[STR-1] All 35 blocks added successfully. Proceeding to Publish...")
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
