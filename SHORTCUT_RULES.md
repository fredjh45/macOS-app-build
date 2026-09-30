# Google Sites Automation – Frozen Rules & Shortcut Dictionary

This document serves as the official, permanent reference for all verified, tested, and frozen automation rules for Google Sites.
Each keyword represents an exact, tested sequence in `core/sites_engine.py`.

---

## 🏷️ The 17 Core Shortcut Words (100% Tested & Frozen)

| # | Shortcut Keyword | Target Element | Action & Verification | Underlying Engine Method | Status |
| :-: | :--- | :--- | :--- | :--- | :-: |
| **1** | `H2_THEME` | H2 Heading (Theme Color) | Focused text box -> Native `Control+Alt+2` -> Palette icon -> 3rd color option (`Style 3`). | `automator.add_h2_heading_section(text, section_style="Style 3")` | ✅ Frozen |
| **2** | `BG_THEME` | Section Background Color | Vertical row position lock (`y-coord`) -> Hover row (`x=300`) -> Palette -> Select 3rd option (`Style 3`). | `automator.set_section_color("Style 3")` | ✅ Frozen |
| **3** | `TEXT_BOX` | Normal Text (Multi-paragraph) | Windows OS Clipboard API (`ctypes` + `CF_UNICODETEXT`) -> Click box -> `Control+V` -> Paragraph persistence. | `automator.add_normal_text_box(paragraphs)` | ✅ Frozen |
| **4** | `LINE_GUARD` | Line-by-Line Structure Guard | Checks active box; if filled, deselects with `Escape` before inserting next item to prevent heading/paragraph merge. | `automator._prepare_canvas_for_new_section()` | ✅ Frozen |
| **5** | `IMG_FULL` | Image (12-Column Full Width) | Uploads image -> Detects `div.aGAaLb` East handle -> Smooth 18-step mouse drag to `target_x = 970px` (magnetic snap) -> Clicks `Uncrop` -> `Escape`. | `automator.add_image_element(image_path, make_full_width=True)` | ✅ Frozen |
| **6** | `MAP_FULL` | Google Map Embed (Full Width) | Map widget -> Enters query -> Selects suggestion -> Clicks picker `Select` button -> Smooth 18-step drag to `target_x = 970px` (779px full width). | `automator.add_map_embed(query, make_full_width=True)` | ✅ Frozen |
| **7** | `BTN_FULL` | Button (12-Column Full Width) | Button widget -> Enters Label & Link -> Smooth 18-step drag of East handle to `target_x = 970px` (spans all 12 columns). | `automator.add_button_element(label, link, make_full_width=True)` | ✅ Frozen |
| **8** | `BTN_HEADER` | Header Docked Button | Button widget -> Enters Label & Link -> Smooth 35-step upward drag directly under page title inside header banner -> Blue guide line snap -> Docks in banner under title. | `automator.add_button_element(label, link, drag_to_header=True)` | ✅ Frozen |
| **9** | `BG_HEADER` | Header Background Image | Hovers top banner -> Clicks `Image` toolbar dropdown -> Clicks `Upload` -> Sends image file via file chooser -> Updates hero banner background. | `automator.set_header_background_image(image_path)` | ✅ Frozen |
| **10** | `BLOCK_1` *(or `CB_1`)* | Content Block 1 (Left Image + Right Text) | Clicks 1st layout card -> Uploads image into left '+' placeholder -> Pastes Heading into top text gridcell -> Pastes Normal text into bottom description gridcell. | `automator.add_content_block_1(image_path, title_text, body_text, section_style=None)` | ✅ Frozen |
| **11** | `BLOCK_2` *(or `CB_2`)* | Content Block 2 (2 Equal Columns) | Clicks 2nd layout card -> Uploads Image 1 & Image 2 into both placeholders -> Pastes Title & Description in Column 1 -> Pastes Title & Description in Column 2. | `automator.add_content_block_2(items, section_style=None)` | ✅ Frozen |
| **12** | `BLOCK_3` *(or `CB_3`)* | Content Block 3 (Collage: 3 Images) | Clicks 3rd layout card -> Uploads 3 images (2 stacked left + 1 large right) into canvas collage layout without distortion. | `automator.add_content_block_3(image_paths, section_style=None)` | ✅ Frozen |
| **13** | `BLOCK_4` *(or `CB_4`)* | Content Block 4 (3 Equal Columns) | Clicks 4th layout card -> Uploads 3 images into each column -> Pastes Title & Description across all 3 columns. | `automator.add_content_block_4(items, section_style=None)` | ✅ Frozen |
| **14** | `BLOCK_5` *(or `CB_5`)* | Content Block 5 (Dual Horizontal Cards) | Clicks 5th layout card -> Uploads 2 images into both horizontal card thumbnails -> Pastes Title & Description in Card 1 -> Pastes Title & Description in Card 2. | `automator.add_content_block_5(items, section_style=None)` | ✅ Frozen |
| **15** | `BLOCK_6` *(or `CB_6`)* | Content Block 6 (4 Column Showcase) | Clicks 6th layout card -> Uploads 4 images into each column thumbnail -> Pastes Caption/Title across all 4 columns. | `automator.add_content_block_6(items, section_style=None)` | ✅ Frozen |
| **16** | `THEME` *(or `SITE_THEME`)* | Google Sites Theme Selection | Clicks `Themes` tab -> Scrolls and selects theme from *Created by Google* (Simple, Aristotle, Diplomat, Vision, Level, Impression) -> Optionally selects palette color (1-5) -> Returns to `Insert` tab. | `automator.select_google_theme(theme_name, color_index=1)` | ✅ Frozen |
| **17** | `ANNOUNCEMENT` *(or `TOP_BANNER`)* | Top Announcement Banner | Clicks Settings gear -> Clicks `Announcement banner` -> Toggles switch ON -> Fills Message text (up to 150 chars) -> Sets CTA button label & link (`tel:` / `https:`) -> Sets 'All pages' -> Closes dialog. | `automator.set_announcement_banner(message, button_label, link)` | ✅ Frozen |

---

## 📌 Secondary / Auxiliary Shortcuts

| Shortcut Keyword | Description | Underlying Engine Method | Status |
| :--- | :--- | :--- | :-: |
| `H2_PLAIN` | H2 Heading with plain/transparent background (no color change) | `automator.add_h2_heading_section(text, section_style=None)` | ✅ Ready |
| `KEYWORDS_BOX` | Standalone bulk SEO keywords text box at bottom | `automator.add_bulk_keywords_box(keywords_text)` | ✅ Ready |
| `FOOTER` | Custom site-wide footer text | `automator.add_footer(footer_text)` | ✅ Ready |
| `PUBLISH` | Validates slug, publishes site and returns live URL | `automator.publish_and_get_url(keyword)` | ✅ Ready |

---

## 📝 Syntax Examples for User & Agent

When requesting or generating page structures, use the shortcuts directly:

```text
Structure Definition Example:
1. BTN_HEADER: "Chat on WhatsApp", "https://wa.me/919876543210"
2. H2_THEME: "Professional Pest Control Services in Dehradun"
3. TEXT_BOX: [para1, para2, para3]
4. IMG_FULL: "images/service_feature.jpg"
5. H2_THEME: "Why Choose Our Termite & Pest Treatments"
6. TEXT_BOX: [para4, para5]
7. BTN_FULL: "Call Now: +91 9876543210", "tel:+919876543210"
8. MAP_FULL: "Dehradun, Uttarakhand, India"
9. KEYWORDS_BOX: "pest control, termite control, dehradun exterminator"
10. PUBLISH
```

---
*All 17 rules above are verified, visually confirmed on interactive desktop, and permanently frozen.*
