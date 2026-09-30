"""
Custom Structure: Handles publishing of manual custom content.
Layout rule:
TITLE (Document Name & Header Title)
BTN_FULL (Phone Number Call Button)
BTN_FULL (WhatsApp Link Button)
TEXT_BOX (Single Text Box with all Editor Content)
PUBLISH
"""

import re
import os
from typing import Optional

STRUCTURE_ID = "str-custom"
STRUCTURE_NAME = "Custom Content Structure"
IMAGE_FOLDER_NAME = "str-image1"
DESCRIPTION = "Header Title -> Full-Width Call Button -> Full-Width WhatsApp Button -> Single Content Text Box -> Publish"

def execute_structure_custom(
    automator,
    title: str,
    phone_number: str,
    whatsapp_link: str,
    custom_content: str,
    theme_name: str = "Simple",
    theme_color_hex: Optional[str] = None,
    enable_announcement: bool = False,
    announcement_message: Optional[str] = None,
    banner_color: Optional[str] = "#FF0000"
) -> Optional[str]:
    """
    Executes Custom Structure on Google Sites:
    1. TITLE: Sets Document Name and Header Title to title
    2. BTN_FULL: Inserts full-width 'Call Now' button on canvas
    3. BTN_FULL: Inserts full-width 'WhatsApp Now' button on canvas
    4. TEXT_BOX: Inserts single text box and pastes all custom editor content
    5. PUBLISH: Publishes site and returns live URL
    """
    automator.log(f"[STR-CUSTOM] Starting Custom Structure workflow for title: '{title}'...")

    # 1. Format Phone URL and WhatsApp URL
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

    # 2. Create blank site
    if not automator.create_blank_site():
        automator.log("[STR-CUSTOM] [ERROR] Failed to create blank site.")
        return None

    # 3. Select Theme
    target_theme = theme_name or "Simple"
    automator.select_google_theme(target_theme)

    # 4. Announcement banner (if enabled)
    if enable_announcement:
        banner_msg = announcement_message or f"24/7 Available for {title.title()} - Contact Now"
        automator.set_announcement_banner(
            message=banner_msg,
            button_label="Call Now",
            link=tel_url
        )

    # 5. TITLE: Set Document/Website Name and Header Title
    automator.log(f"[STR-CUSTOM] [TITLE] Setting Document Name and Header Title to: '{title}'...")
    automator.set_document_name(title)
    automator.set_header_title(title, enforce_length=False)

    # 6. BTN_FULL: Button 1 (Phone Number) on Canvas
    automator.log(f"[STR-CUSTOM] [BTN_FULL] Adding Full-Width Phone Button ('Call Now')...")
    automator.add_button_element("Call Now", tel_url, make_full_width=True, drag_to_header=False)

    # 7. BTN_FULL: Button 2 (WhatsApp Link) on Canvas
    automator.log(f"[STR-CUSTOM] [BTN_FULL] Adding Full-Width WhatsApp Button ('WhatsApp Now')...")
    automator.add_button_element("WhatsApp Now", wa_clean, make_full_width=True, drag_to_header=False)

    # 8. TEXT_BOX: Single Text Box with all custom editor content
    automator.log(f"[STR-CUSTOM] [TEXT_BOX] Adding single Text Box with custom content...")
    if custom_content and custom_content.strip():
        paragraphs = [p.strip() for p in custom_content.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [custom_content.strip()]
    else:
        paragraphs = [f"Welcome to {title}. Contact us for genuine, reliable and professional services."]

    automator.add_normal_text_box(paragraphs)

    # 9. PUBLISH: Publish site & return verified live URL
    automator.log("[STR-CUSTOM] All elements added successfully. Proceeding to Publish...")
    pub_url = automator.publish_and_get_url(title)

    from database.db import add_task_history
    add_task_history(
        keyword=title,
        structure_used=STRUCTURE_NAME,
        phone_number=phone_number,
        whatsapp_link=whatsapp_link,
        published_url=pub_url or "",
        status="SUCCESS" if pub_url else "FAILED"
    )
    return pub_url

# Backward/dynamic compatibility alias
execute_str_custom = execute_structure_custom

