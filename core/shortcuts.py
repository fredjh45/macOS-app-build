"""
Standard Shortcut Rules and Grammar for Google Sites Automation.
Maps user shorthand keywords directly to tested, frozen automation engine actions.
"""

SHORTCUTS = {
    'H2_THEME': {
        'name': 'H2 Heading with Theme Background (Style 3)',
        'method': 'add_h2_heading_section',
        'default_kwargs': {'section_style': 'Style 3'},
    },
    'H2_PLAIN': {
        'name': 'H2 Heading with Plain Background',
        'method': 'add_h2_heading_section',
        'default_kwargs': {'section_style': None},
    },
    'BG_THEME': {
        'name': 'Current Section Row Theme Color (Style 3)',
        'method': 'set_section_color',
        'default_kwargs': {'style_name': 'Style 3'},
    },
    'TEXT_BOX': {
        'name': 'Normal Text Box (OS Clipboard Paste + Persistence)',
        'method': 'add_normal_text_box',
    },
    'LINE_GUARD': {
        'name': 'Empty Box Guard (Deselect to prevent merge)',
        'method': '_prepare_canvas_for_new_section',
    },
    'IMG_FULL': {
        'name': 'Image stretched across 12-column grid + Uncrop',
        'method': 'add_image_element',
        'default_kwargs': {'make_full_width': True},
    },
    'MAP_FULL': {
        'name': 'Google Maps Embed stretched across 12-column grid',
        'method': 'add_map_embed',
        'default_kwargs': {'make_full_width': True},
    },
    'BTN_FULL': {
        'name': 'Call/Action Button stretched across 12-column grid',
        'method': 'add_button_element',
        'default_kwargs': {'make_full_width': True},
    },
    'BTN_HEADER': {
        'name': 'Button docked into Header Banner under Title',
        'method': 'add_button_element',
        'default_kwargs': {'drag_to_header': True},
    },
    'BG_HEADER': {
        'name': 'Upload custom background image into Header Banner',
        'method': 'set_header_background_image',
    },
    'HEADER_BG': {
        'name': 'Upload custom background image into Header Banner (alias)',
        'method': 'set_header_background_image',
    },
    'BLOCK_1': {
        'name': 'Content Block 1 (Left Image + Right Title & Description)',
        'method': 'add_content_block_1',
    },
    'CB_1': {
        'name': 'Content Block 1 (alias)',
        'method': 'add_content_block_1',
    },
    'BLOCK_2': {
        'name': 'Content Block 2 (2 Equal Columns: Image + Title + Description each)',
        'method': 'add_content_block_2',
    },
    'CB_2': {
        'name': 'Content Block 2 (alias)',
        'method': 'add_content_block_2',
    },
    'BLOCK_3': {
        'name': 'Content Block 3 (Collage: 2 Small Images Left + 1 Large Image Right)',
        'method': 'add_content_block_3',
    },
    'CB_3': {
        'name': 'Content Block 3 (alias)',
        'method': 'add_content_block_3',
    },
    'BLOCK_4': {
        'name': 'Content Block 4 (3 Equal Columns: Image + Title + Description each)',
        'method': 'add_content_block_4',
    },
    'CB_4': {
        'name': 'Content Block 4 (alias)',
        'method': 'add_content_block_4',
    },
    'BLOCK_5': {
        'name': 'Content Block 5 (Dual Horizontal Cards: Image Left + Text Right)',
        'method': 'add_content_block_5',
    },
    'CB_5': {
        'name': 'Content Block 5 (alias)',
        'method': 'add_content_block_5',
    },
    'BLOCK_6': {
        'name': 'Content Block 6 (4 Columns: Image + Caption each)',
        'method': 'add_content_block_6',
    },
    'CB_6': {
        'name': 'Content Block 6 (alias)',
        'method': 'add_content_block_6',
    },
    'THEME': {
        'name': 'Google Sites Theme Selection (Created by Google)',
        'method': 'select_google_theme',
        'default_kwargs': {'theme_name': 'Aristotle', 'color_index': 1},
    },
    'SITE_THEME': {
        'name': 'Google Sites Theme Selection (alias)',
        'method': 'select_google_theme',
        'default_kwargs': {'theme_name': 'Aristotle', 'color_index': 1},
    },
    'ANNOUNCEMENT': {
        'name': 'Announcement Banner (Top of page banner with message, button & link)',
        'method': 'set_announcement_banner',
    },
    'TOP_BANNER': {
        'name': 'Announcement Banner (alias)',
        'method': 'set_announcement_banner',
    },
    'KEYWORDS_BOX': {
        'name': 'Bulk SEO Keywords text box',
        'method': 'add_bulk_keywords_box',
    },
    'FOOTER': {
        'name': 'Footer text block',
        'method': 'add_footer',
    },
    'PUBLISH': {
        'name': 'Publish Site and get live URL',
        'method': 'publish_and_get_url',
    },
}
