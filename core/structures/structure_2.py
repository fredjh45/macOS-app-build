"""
Structure 2: High-Speed Clean Content & Dual Header CTA
Layout (derived from visual template analysis):
1. Hero Section (Header Banner):
   - Background Image (from images/str-image2/)
   - H1: Title featuring target keyword
   - Button 1: 'WhatsApp' docked in header under title
   - Button 2: 'Call me' docked in header
2. Section 1: H2 Heading (Plain Background) + 2 Paragraphs
3. Section 2: H2 Heading (Plain Background) + 1 Paragraph
4. Section 3: H2 Heading (Plain Background) + 2 Paragraphs
5. Section 4: H2 Heading (Plain Background) + 2 Paragraphs
6. Section 5: H2 Heading (Plain Background) + 1 Paragraph
7. Section 6: H2 Heading (Plain Background) + 1 Paragraph
8. Section 7: H2 Heading (Plain Background) + 2 Paragraphs
9. Section 8: H2 Heading (Plain Background) + 2 Paragraphs
10. Tag Keywords: H2 'Tag keywords –' + Bulk Keywords Text Box
11. Map: Google Maps Embed (Full Width)
12. Publish: Slug validation, publish confirmation & live URL extraction
"""

import os
import re
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional
logger = logging.getLogger(__name__)

STRUCTURE_ID = "str-2"
STRUCTURE_NAME = "Structure 2: High-Speed Clean Content & Dual Header CTA"
IMAGE_FOLDER_NAME = "str-image2"
DESCRIPTION = "Hero (Bg Image + H1 + 2 Docked Header Buttons: WhatsApp & Call) -> 8 Plain H2 Headings + Text Paragraphs -> Tag Keywords Box -> Google Maps"


import random
from core.location_helper import extract_location_and_map_query, generate_comprehensive_tag_keywords

def generate_dynamic_structure_2_title(keyword: str, city: Optional[str] = None) -> str:
    """Generates dynamic multi-part title matching Image 1: [City] [Keyword] - [Contact/Badge] | [Authority Adjective] [Keyword] & [Premium Hub]."""
    kw = keyword.strip().title()
    if not city:
        city, _ = extract_location_and_map_query(keyword)
    badges = [
        "24/7 Available", "Instant WhatsApp Booking", "Direct Cash Payment",
        "Doorstep Arrival in 20 Mins", "Verified Independent Girls",
        "100% Safe & Confidential", "Top Rated Agency", "Genuine VIP Service"
    ]
    adjectives = [
        "Best", "Top Rated", "Premier", "Elite VIP", "Highly Acclaimed",
        "Number #1", "Most Trusted", "5-Star Luxury"
    ]
    hubs = [
        f"VIP Escorts in {city}", f"Doorstep Companions in {city}",
        f"Elite Escort Agency {city}", f"Hot College Girls Hub",
        f"Russian & Celebrity Models in {city}", f"Independent Service {city}"
    ]
    badge = random.choice(badges)
    adj = random.choice(adjectives)
    hub = random.choice(hubs)
    raw_title = f"{city} {kw} - {badge} | {adj} {kw} & {hub}"
    from core.sites_engine import enforce_title_60_70
    return enforce_title_60_70(raw_title, kw)


def build_structure_2_prompt(keyword: str, related_keywords: Optional[List[str]] = None) -> str:
    """Builds the AI prompt for Structure 2 (8 plain sections with exact 2-1-2-2-1-1-2-2 paragraph layout + Tag Keywords)."""
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

    prompt = f"""You are an elite SEO content writer for a high-converting Google Sites local service webpage.
Generate complete structured text content following the EXACT 8-section layout below for keyword: '{keyword}'.

CRITICAL RULES:
1. Do NOT include hyperlinks, URLs, phone numbers, or WhatsApp numbers in the body paragraphs.
2. Target keywords: {kw_string}
   Naturally integrate them across headings and paragraphs.
3. Return pure, valid JSON only. Do not wrap with markdown code blocks.
4. h1_title LENGTH RULE: 'h1_title' MUST be STRICTLY between 60 and 70 characters long (including spaces). Never make it shorter than 60 or longer than 70 characters.
5. STRICT WORD COUNT REQUIREMENTS PER SECTION:
   - Section 3 & Section 4: MUST HAVE TOTAL 250 - 260 WORDS EACH! (Split evenly across 2 paragraphs: ~125 - 130 words per paragraph).
   - All Other Sections (1, 2, 5, 6, 7, 8): MUST HAVE TOTAL 150 - 160 WORDS EACH!
     * Section 1: 2 Paragraphs (~75 - 80 words each, combined 150 - 160 words).
     * Section 2: 1 Paragraph (Solid block of 150 - 160 words).
     * Section 5: 1 Paragraph (Solid block of 150 - 160 words).
     * Section 6: 1 Paragraph (Solid block of 150 - 160 words).
     * Section 7: 2 Paragraphs (~75 - 80 words each, combined 150 - 160 words).
     * Section 8: 2 Paragraphs (~75 - 80 words each, combined 150 - 160 words).
6. EXACT PARAGRAPH DISTRIBUTION PER SECTION:
   - Section 1: EXACTLY 2 PARAGRAPHS (Total 150 - 160 words)
   - Section 2: EXACTLY 1 PARAGRAPH (Total 150 - 160 words)
   - Section 3: EXACTLY 2 PARAGRAPHS (Total 250 - 260 words, Multi-query / Hindi & English mix heading)
   - Section 4: EXACTLY 2 PARAGRAPHS (Total 250 - 260 words, Price/offer specific Hindi & English mix heading)
   - Section 5: EXACTLY 1 PARAGRAPH (Total 150 - 160 words)
   - Section 6: EXACTLY 1 PARAGRAPH (Total 150 - 160 words)
   - Section 7: EXACTLY 2 PARAGRAPHS (Total 150 - 160 words)
   - Section 8: EXACTLY 2 PARAGRAPHS (Total 150 - 160 words)

Structure Requirements:
1. h1_title: An eye-catching multi-part title strictly between 60 and 70 characters:
   Format: '[City] [Keyword] - [Contact/Badge] | [Authority Adjective] [Keyword] & [Premium Hub]' (Strictly 60-70 characters total)
   Reference Example: '{city} Escort Service - 24/7 Available | Best Escort Service & VIP'
   CRITICAL: Dynamically vary the badge, superlative adjective, and secondary hub phrase on EVERY generation so the title is unique and captivating!
2. sections: Exactly 8 sections matching the exact paragraph counts (2, 1, 2, 2, 1, 1, 2, 2) and word counts.
3. bulk_keywords: 60-80 comma-separated related search queries and tags (~200-300 words).
4. map_query: Specific city or locality for '{keyword}' (e.g. '{map_query}').

Schema:
{{
    "h1_title": "{city} {keyword.title()} - 24/7 Available | Best {keyword.title()} & VIP Escorts in {city}",
    "sections": [
        {{"h2": "Find Your Desired Companions For Direct Cash Payment in {city}", "paragraphs": ["Para 1 (75-80 words)...", "Para 2 (75-80 words)..."]}},
        {{"h2": "Special Offers and High Profile Profiles in {city}", "paragraphs": ["Para 1 (150-160 words)..."]}},
        {{"h2": "Updated WhatsApp Contact and Round The Clock Booking | 24/7 सेवा उपलब्ध", "paragraphs": ["Para 1 (125-130 words)...", "Para 2 (125-130 words)..."]}},
        {{"h2": "Affordable Price Packages Just In A Phone Call | बेस्ट रेट और डिस्काउंट", "paragraphs": ["Para 1 (125-130 words)...", "Para 2 (125-130 words)..."]}},
        {{"h2": "Top Verified and Discreet Independent Companions", "paragraphs": ["Para 1 (150-160 words)..."]}},
        {{"h2": "Everything You Should Know About Our Doorstep Service", "paragraphs": ["Para 1 (150-160 words)..."]}},
        {{"h2": "Book The Perfect Companion Near Me Within 20 Minutes", "paragraphs": ["Para 1 (75-80 words)...", "Para 2 (75-80 words)..."]}},
        {{"h2": "Exclusive Benefits And Complete Privacy Guarantee", "paragraphs": ["Para 1 (75-80 words)...", "Para 2 (75-80 words)..."]}}
    ],
    "bulk_keywords": "{keyword}, {keyword} Near Me, Best {keyword} in {city}, Affordable {keyword} in {city}, 24/7 {keyword}...",
    "map_query": "{map_query}"
}}
"""
    return prompt


def generate_structure_2_content(keyword: str, related_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generates AI content for Structure 2 using DeepSeek / Grok with robust fallback."""
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
        logger.warning(f"[STR-2] No API key found for {provider}. Using fallback content.")
        return get_structure_2_fallback(keyword, related_keywords)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_structure_2_prompt(keyword, related_keywords)},
            {"role": "user", "content": f"Generate Structure 2 content for: '{keyword}' now."}
        ],
        "temperature": 0.7,
        "max_tokens": 5000
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
            logger.error(f"[STR-2] API Error {r.status_code}: {r.text[:200]}")
            return get_structure_2_fallback(keyword, related_keywords)
    except Exception as e:
        logger.exception(f"[STR-2] Exception during AI generation: {e}")
        return get_structure_2_fallback(keyword, related_keywords)


def get_structure_2_fallback(keyword: str, related_keywords: Optional[List[str]] = None, city: Optional[str] = None) -> Dict[str, Any]:
    """Fallback adhering strictly to Structure 2 layout matching Image 1 with exact word targets (Sec 3 & 4: 250-260 words, Others: 150-160 words)."""
    if not city:
        city, map_query = extract_location_and_map_query(keyword)
    else:
        _, map_query = extract_location_and_map_query(f"{keyword} {city}")
    kw_title = keyword.strip().title()
    h1 = generate_dynamic_structure_2_title(keyword, city=city)

    sections = [
        {
            "h2": f"Find Your Desired Companions For Direct Cash Payment in {kw_title}",
            "paragraphs": [
                f"Finding reliable, genuine, and high-class {keyword} near your locality requires trusted professionalism, absolute discretion, and utmost dedication to client satisfaction across every visit. Our premier network connects you directly with charming, sophisticated, and verified independent companions who excel in providing unmatched warmth, elegance, delightful company, and memorable experiences. Whether you are visiting the city for business conferences, leisure retreats, or seeking peaceful private relaxation, our experienced team ensures your companionship journey is tailored to perfection with uncompromising care.",
                f"We maintain exemplary standards of hospitality and security, ensuring every interaction is completely private, safe, and hassle-free from start to finish for all valued guests. Our esteemed patrons enjoy seamless booking assistance, prompt doorstep coordination, and complete pricing transparency without unexpected complications. With verified authentic profiles, real photographs, and polite communication, your time spent with our elite companions will be wonderfully comfortable, refreshing, and thoroughly memorable on every appointment throughout {city}."
            ]
        },
        {
            "h2": f"Special Offers and High Profile Profiles in {kw_title}",
            "paragraphs": [
                f"Take advantage of our exclusive promotional packages and premier selection of high-profile companions curated specifically for discerning clients who appreciate luxury, refined company, and effortless comfort. We take immense pride in offering an impressive variety of verified independent profiles, ranging from charming college models to sophisticated corporate hostesses, all dedicated to elevating your leisure hours. Each booking comes with straightforward transparent terms, zero hidden charges, and complete flexibility regarding convenient timing and preferred private venues. Whether you prefer an intimate private dinner date, an upscale social event escort, or relaxing hotel room company after long travels, our tailored arrangements guarantee unmatched elegance and genuine satisfaction at unbeatable value. Contact our responsive customer desk today to browse available options, check immediate schedules, and lock in exciting discounted rates designed to provide maximum enjoyment, complete peace of mind, and truly unforgettable memories on every private interaction with our premier agency in {city}."
            ]
        },
        {
            "h2": f"Updated WhatsApp Contact and Round The Clock Booking | 24/7 सेवा उपलब्ध",
            "paragraphs": [
                f"Connecting with our direct customer support team is instantaneous, secure, and accessible round the clock through dedicated WhatsApp messaging and priority voice calls. We recognize that our valued patrons frequently lead demanding, fast-paced lifestyles where convenience, absolute privacy, and rapid responses are paramount, which is why our reservations desk remains fully active 24 hours a day, 7 days a week. From answering preliminary inquiries regarding profile availability, genuine photos, and service specifics to coordinating seamless doorstep arrivals at premier luxury hotels or private residential bungalows, our coordinators manage every facet with total professionalism and utmost confidentiality. You will never encounter automated answering bots or prolonged waiting intervals; our real-time operators communicate clearly, respectfully, and helpfully to confirm your reservations swiftly without any friction or unnecessary delays whatsoever.",
                f"हमारी 24/7 एक्टिव व्हाट्सएप और कॉलिंग सेवा आपको बिना किसी अग्रिम भुगतान के सीधी बुकिंग की पूर्ण सुविधा प्रदान करती है। आप किसी भी समय अपनी पसंद की स्वतंत्र प्रोफाइल के बारे में विस्तृत जानकारी प्राप्त कर सकते हैं और केवल कुछ ही संदेशों में अपना पसंदीदा समय और स्थान सुरक्षित कर सकते हैं। We prioritize your comfort by offering flexible communication protocols, ensuring that your personal identity, telephone number, and booking details are protected at all stages of contact. Whether you are planning well in advance for an upcoming weekend getaway or need immediate companionship after a stressful day of travel, our prompt team ensures immediate assistance, verified profiles, and seamless coordination across all prime central locations, resorts, and luxury hotels throughout the city."
            ]
        },
        {
            "h2": f"Affordable Price Packages Just In A Phone Call | बेस्ट रेट और डिस्काउंट",
            "paragraphs": [
                f"We firmly believe that world-class companionship should always be accompanied by transparent, competitive, and clearly structured pricing packages that deliver exceptional value without unpleasant surprises, hidden conditions, or confusing terms. Our agency provides comprehensive tariff options tailored to diverse preferences and unique requirements, including short-duration evening sessions, extended romantic dinner dates, corporate dinner accompaniments, and luxurious overnight stays. Every quotation provided by our customer desk is all-inclusive, covering genuine hospitality and verified arrangements without any hidden administrative surcharges or unexpected last-minute demands. We maintain complete clarity upfront so you can focus entirely on enjoying a relaxing, fulfilling time with your chosen companion, confident that you are receiving the finest standard of service at rates that genuinely reflect premium quality, respect, trust, and absolute professional integrity.",
                f"बेस्ट रेट्स, स्पेशल डिस्काउंट और 100% डायरेक्ट कैश ऑन डिलीवरी भुगतान की सुविधा हमारे सभी ग्राहकों के लिए हमेशा उपलब्ध है। आपको किसी भी प्रकार का अग्रिम या एडवांस भुगतान करने की आवश्यकता बिल्कुल नहीं होती है; आप सेवा से पूरी तरह संतुष्ट होने के बाद सीधे कैश में सुरक्षित भुगतान कर सकते हैं। This customer-first approach eliminates financial uncertainties and builds lasting trust with our clients. Moreover, we regularly introduce seasonal promotional deals, customized corporate discounts, and privileged package rates for returning guests, making premium luxury companionship both accessible, remarkably budget-friendly, and exceptionally rewarding whenever you choose to spend your valuable private time with our agency in our vibrant city. Simply ask our desk representatives for current ongoing festive specials and customized packages tailored specifically to your duration and venue preferences."
            ]
        },
        {
            "h2": f"Top Verified and Discreet Independent Companions in {city}",
            "paragraphs": [
                f"Every independent companion featured within our agency roster undergoes meticulous personal screening, comprehensive background verification, and detailed health checks to ensure outstanding personal grooming, genuine charm, and complete authenticity across every single parameter. We hold our entire network to stringent benchmarks of professionalism, polite etiquette, and discreet behavior, guaranteeing that your encounters are characterized by mutual respect, warmth, sophistication, and complete peace of mind at all times without fail. Our companions possess exceptional conversational abilities, refined social manners, and attentive demeanors, making them ideal partners for high-profile corporate gatherings as well as private relaxation sessions in the quiet comfort of your private quarters. When you reserve through our platform, you receive verified photographs and authentic profile details, giving you absolute certainty and total confidence that your expectations will be matched precisely with elegance, warmth, and grace throughout your entire booking session with our agency without any doubts, misunderstandings, or hesitation."
            ]
        },
        {
            "h2": f"Everything You Should Know About Our Doorstep Service",
            "paragraphs": [
                f"Understanding the practical procedures of our doorstep service allows you to enjoy an effortlessly smooth, comfortable, and stress-free appointment from initial booking confirmation to final departure. Once your reservation details are finalized with our dispatch team, our companion arrives promptly at your chosen location, whether that is a luxury five-star hotel room, a boutique resort, or your personal private apartment. We coordinate travel logistics discreetly, ensuring zero unwanted attention, awkward delays, or interruptions at reception desks or residential premises. Our companions prioritize impeccable personal hygiene, respectful interpersonal boundaries, gentle manners, and complete confidentiality, creating a comfortable private sanctuary where you can unwind in complete safety, comfort, and peaceful luxury without any external disturbances, worries, unexpected costs, or awkward moments at any point during your booking, making it truly effortless, deeply satisfying, and completely confidential for every single esteemed guest who honors us with their trust, valued patronage, and continuous preference."
            ]
        },
        {
            "h2": f"Book The Perfect Companion Near Me Within 20 Minutes in {city}",
            "paragraphs": [
                f"When time is of the essence, our strategically positioned network ensures ultra-fast doorstep dispatch to your preferred location within 20 to 30 minutes of confirmation. We maintain active associate hubs across all major sectors, commercial zones, and hospitality corridors, eliminating frustrating transit delays and enabling spontaneous bookings whenever you desire. Whether you find yourself relaxing in a downtown hotel or residing in upscale suburbs, our rapid coordination team handles routing with military precision, quiet professionalism, and absolute discretion.",
                f"You can effortlessly schedule immediate arrivals by dropping a quick ping on WhatsApp or making a brief phone call to our active desk representatives. Our drivers and associates operate with complete discretion, ensuring quiet and unassuming arrivals that blend seamlessly into any hotel or residential environment. Experience the immense convenience of prompt, on-demand luxury companionship that arrives exactly when you need it without making you wait or disrupting your precious schedule in any way."
            ]
        },
        {
            "h2": f"Exclusive Benefits And Complete Privacy Guarantee in {city}",
            "paragraphs": [
                f"Choosing our premier agency grants you access to an unparalleled array of exclusive privileges, bespoke amenities, and ironclad privacy safeguards developed through years of dedicated service. We recognize that discretion is the single most crucial factor for our high-profile clientele, and we enforce rigorous non-disclosure protocols across all communications, records, and interactions. Your private information is never retained, shared, or compromised under any circumstance whatsoever at any stage of our engagement.",
                f"From customizable itineraries to personalized hospitality touches, we strive relentlessly to surpass your highest benchmarks of satisfaction, relaxation, and leisure across all fronts. Contact our dedicated support desk today via WhatsApp or direct telephone call to begin your journey with the most trusted, dependable, and lavish companionship service available across the entire region, complete with transparent cash billing, verified independent profiles, prompt doorstep arrival, polite customer assistance, and total customer satisfaction guaranteed on every visit with our courteous coordinators."
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


def execute_structure_2(
    automator,
    keyword: str,
    phone_number: str,
    whatsapp_link: str,
    ai_content: Optional[Dict[str, Any]] = None,
    related_keywords: Optional[List[str]] = None,
    theme_name: str = "Impression",
    theme_color_hex: Optional[str] = None,
    enable_announcement: bool = False,
    announcement_message: Optional[str] = None,
    banner_color: Optional[str] = "#FF0000",
    use_demo_content: bool = False
) -> Optional[str]:
    """
    Executes the exact Structure 2 workflow on Google Sites.
    Layout:
    1. Hero Header Banner (Full Width Background Image)
    2. H1 Title set as document site name & banner title
    3. Two docked buttons inside header banner: 'WhatsApp' & 'Call me'
    4. 8 Plain H2 Headings (H2_PLAIN) + Normal Text Boxes (TEXT_BOX)
    5. 'Tag keywords –' H2 Heading + Bulk Keywords Box (KEYWORDS_BOX)
    6. Google Maps Embed full-width (MAP_FULL)
    7. Publish site & return verified live URL (PUBLISH)
    """
    automator.log("[STR-2] Starting Execution for Structure 2 (Clean Content & Dual Header CTA)...")

    # Dynamic location extraction
    city, default_map = extract_location_and_map_query(keyword)

    # 1. Prepare Content
    if not ai_content:
        if use_demo_content:
            automator.log(f"[STR-2] Using instant fallback content for: '{keyword}' (City: {city})...")
            ai_content = get_structure_2_fallback(keyword, related_keywords, city=city)
        else:
            automator.log(f"[STR-2] Generating AI content for: '{keyword}' (City: {city})...")
            ai_content = generate_structure_2_content(keyword, related_keywords)

    from core.sites_engine import enforce_title_60_70
    h1_title = enforce_title_60_70(ai_content.get("h1_title") or generate_dynamic_structure_2_title(keyword, city=city), keyword)
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
        automator.log("[STR-2] [ERROR] Failed to create blank site.")
        return None

    # Apply Site Theme if specified and not default Simple
    if theme_name and theme_name.strip().lower() != "simple":
        automator.select_google_theme(theme_name)

    # Apply Announcement Banner if enabled
    if enable_announcement:
        banner_msg = announcement_message or f"24/7 Fast Service Available for {keyword.title()} - Contact Now"
        automator.set_announcement_banner(
            message=banner_msg,
            button_label="Call Now",
            link=tel_url
        )

    # ==========================================
    # BLOCK 1: Hero Section (Header Background Image + H1 Title + Dual Docked Buttons)
    # ==========================================
    # 1. Set Header Background Image FIRST (ensures clean compact banner state)
    images = automator.upload_structure_images(IMAGE_FOLDER_NAME)
    if images:
        random.shuffle(images)
    if len(images) > 0:
        hero_img_path = images[0]
        automator.log(f"[STR-2] [HERO] Randomly picked background image: {os.path.basename(hero_img_path)}")
        automator.set_header_background_image(hero_img_path)

    # 2. Set Site Name & Header Title
    automator.log(f"[STR-2] [HERO] Setting Site Name & Header Title to: '{h1_title}'...")
    automator.set_document_name(site_name)
    automator.set_header_title(h1_title)

    # 3. Insert Button 1: 'WhatsApp' docked into Header
    automator.log("[STR-2] [HERO] Docking Button 1 ('WhatsApp') under Header Title...")
    automator.add_button_element("WhatsApp", wa_clean, drag_to_header=True)

    # 4. Insert Button 2: 'Call Now' docked into Header
    automator.log("[STR-2] [HERO] Docking Button 2 ('Call Now') under Header Title...")
    automator.add_button_element("Call Now", tel_url, drag_to_header=True)

    # ==========================================
    # BLOCKS 2 to 9: 8 Plain H2 Sections + Normal Text Boxes
    # ==========================================
    for idx in range(8):
        sec_num = idx + 1
        if idx < len(sections):
            sec = sections[idx]
        else:
            sec = {
                "h2": f"Essential Insights on {keyword.title()} Part {sec_num}",
                "paragraphs": [
                    f"Professional and verified assistance for {keyword}.",
                    f"Fast, discrete, and round the clock execution delivered by industry specialists."
                ]
            }

        automator.log(f"[STR-2] [SECTION {sec_num}/8] Adding H2 Heading (Plain Background): '{sec['h2'][:40]}...'")
        automator.add_h2_heading_section(sec["h2"], section_style=None)  # H2_PLAIN rule

        automator.log(f"[STR-2] [SECTION {sec_num}/8] Adding Normal Text ({len(sec['paragraphs'])} paras)...")
        automator.add_normal_text_box(sec["paragraphs"])

    # ==========================================
    # BLOCK 10: Tag Keywords Section
    # ==========================================
    automator.log("[STR-2] [TAGS] Adding 'Tag keywords –' Section & Bulk Keywords...")
    automator.add_h2_heading_section("Tag keywords –", section_style=None)
    automator.add_bulk_keywords_box(bulk_keywords_text)

    # ==========================================
    # BLOCK 11: Google Maps Embed (Full Width)
    # ==========================================
    automator.log(f"[STR-2] [MAP] Embedding Google Map for: '{map_query}'...")
    automator.add_map_embed(map_query, make_full_width=True)

    # ==========================================
    # BLOCK 12: Publishing & Live URL Extraction
    # ==========================================
    automator.log("[STR-2] All sections added successfully. Proceeding to Publish...")
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
execute_str_2 = execute_structure_2
