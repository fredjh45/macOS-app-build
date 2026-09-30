# Google Sites UI Interaction Reference & Method Store

This document stores the verified, pin-point visual interaction methods for Google Sites automation, based on the UI layout and screenshots.

---

## 1. Text Box Creation & Styling Workflow

### Step 1: Inserting Text Box (Text-box-1)
- **Action**: Click `Text box` under the `Insert` tab on the right sidebar.
- **Selector**: `div[role='button']:has-text('Text box'), [aria-label*='Text box' i]`
- **Result**:
  - A full-width input container with blue borders appears on the canvas.
  - A floating formatting toolbar docks above the text container.
  - Text input area is `div[contenteditable='true']`.

### Step 2: Setting Text Style / Headings (Text-box-2)
- **Action**: Click the first dropdown on the floating toolbar (defaults to `Normal text`).
- **Selector**: `div[aria-label*='Text style' i], div[aria-label*='Normal text' i], div[role='listbox']`
- **Menu Options**:
  - `Title` (H1) -> `div[role='menuitem']:has-text('Title')`
  - `Heading` (H2) -> `div[role='menuitem']:has-text('Heading')`
  - `Subheading` (H3) -> `div[role='menuitem']:has-text('Subheading')`
  - `Normal text` -> `div[role='menuitem']:has-text('Normal text')`
  - `Small text` -> `div[role='menuitem']:has-text('Small text')`

### Step 3: Text Color Changer (Text-box-3)
- **Action**: Click the `A` icon with color bar on the toolbar.
- **Selector**: `div[aria-label*='Text color' i], button[aria-label*='Text color' i]`
- **Result**: Opens the color palette grid to apply custom font colors.

### Step 4: Section Background / Container Tools (Text-box-4)
- **Action**: Hover over or focus the section. On the left outer margin of the section container, a vertical 3-button control bar appears:
  1. Palette Icon (`Section colors`) -> `div[aria-label*='Section colors' i], [data-tooltip*='Section colors' i]`
  2. Duplicate Section Icon -> `div[aria-label*='Duplicate section' i]`
  3. Delete Section Icon (Trash) -> `div[aria-label*='Delete section' i]`

### Step 5: Applying Section Background Color (Text-box-5)
- **Action**: Click the Palette icon (`Section colors`).
- **Popup Menu Options**:
  - `Style 1` (Default light/transparent background): `div[role='menuitem']:has-text('Style 1')`
  - `Style 2` (Subtle accent/tint background): `div[role='menuitem']:has-text('Style 2')`
  - `Style 3` (Solid primary accent background, e.g., dark blue/theme color): `div[role='menuitem']:has-text('Style 3')`
  - `Image` (Upload/Select custom background image for the entire row): `div[role='menuitem']:has-text('Image')`
- **Result**: The whole full-width section background transforms into the chosen style (e.g. solid colored section banner).

---

## 2. Single Image Upload & Full-Width Resizing Workflow

### Step 1: Open Images Menu (Image-3)
- **Action**: Click `Images` button under the `Insert` tab on the right sidebar.
- **Selector**: `div[role='button']:has-text('Images'), [aria-label*='Images' i]`
- **Menu Options**:
  - `Upload` -> `div[role='menuitem']:has-text('Upload'), span:has-text('Upload')`
  - `Select` -> `div[role='menuitem']:has-text('Select'), span:has-text('Select')`

### Step 2: Selecting Image File (Image-1)
- **Action**: Clicking `Upload` triggers the OS File Chooser.
- **Playwright Handling**: Intercepted using `page.expect_file_chooser()` and file is passed directly via `file_chooser.set_files(image_path)`.

### Step 3: Default Placement on Canvas (Image-2)
- **Result**: Image lands on the canvas, initially taking up roughly 4 columns of the 12-column grid.
- **Selection State**: Surrounded by blue border with corner & side resize dots (handles) and floating toolbar (Crop, Uncrop, Link, Delete, More options).

### Step 4: Dragging to Full Width (Image-4)
- **Action**: Grab the right edge / bottom-right resize handle (blue dot circle).
- **Behavior**: When dragging begins, vertical grid lines (all 12 layout columns) automatically reveal themselves across the canvas.
- **Target**: Drag the cursor horizontally towards the rightmost 12th column grid boundary.

### Step 5: Dragging across the 12 Grid Columns (Image-5)
- **Target**: The blue circle handle is dragged horizontally to the 12th rightmost column guide.
- **Behavior**: The image stretches cleanly across the full container width.

### Step 6: Final Full-Width Image View (Final View)
- **Result**: The image occupies the complete horizontal row cleanly, spanning from the left grid border to the right grid border.
- **Floating Controls**: Floating toolbar sits on the top-left corner (`Crop`, `Uncrop`, `Insert link`, `Duplicate`, `Delete`, `More`).
- **Deselection**: Clicking canvas or pressing `Escape` removes the blue selection boundary, leaving the static, professional full-width image ready on the page.

---

## 3. Embed Component Workflow (By URL & Embed Code)

### Step 1: Open Embed Modal (embed-1)
- **Action**: Click `Embed` button under `Insert` tab on right sidebar.
- **Selector**: `div[role='button']:has-text('Embed'), [aria-label*='Embed' i]`
- **Result**: Modal titled "Embed from the web" opens with two tabs: `By URL` and `Embed code`.

### Step 2: Embed Option A - By URL (embed-2)
- **Active Tab**: `div[role='tab']:has-text('By URL')`
- **Input Field**: `input[type='text'], input[aria-label*='URL' i]`
- **Supported URLs**: Direct media URLs (`.jpg`, `.png`, `.webp`), document links (`.pdf`), or live page URLs.
- **Action**: Fill URL -> Click `Insert` button (`button:has-text('Insert')`).

### Step 3: Embed Option B - Embed Code / Custom HTML (embed-3)
- **Target Tab**: `div[role='tab']:has-text('Embed code')`
- **Input Field**: `textarea` with placeholder `HTML code goes here`.
- **Supported Content**: Custom HTML snippets, iframe embeds, external widgets, lead forms.
- **Workflow**:
  1. Click `Embed code` tab.
  2. Paste HTML code into textarea.
  3. Click `Next` (`button:has-text('Next')`).
  4. Preview screen renders -> Click `Insert` (`button:has-text('Insert')`).

### Step 4: Canvas Placement & Full-Width Resizing (embed-4)
- **Canvas State**: Embedded element appears on the canvas with blue bounding box, corner/edge handles, and edit (pencil) / delete (trash) toolbar.
- **Resizing**: Follows the exact same 12-column grid dragging rule as images:
  - Drag right/bottom-right handle across to the 12th vertical grid boundary to make it Full Width.
  - Press `Escape` or click canvas to deselect handles.

---

## 4. Complete Reference: All 6 Content Blocks (Layouts 1 to 6)

### Block 1: Single Feature Hero Block (Row 1, Card 1)
- **Canvas Layout**: Left large image placeholder + right 2 separate text boxes (Title & Description).

### Block 2: Two-Column Comparison / Feature Block (Row 1, Card 2)
- **Canvas Layout**: 2 equal 50%-50% columns (Image + Title + Description each).

### Block 3: Asymmetric Image Collage / Gallery Block (Row 2, Card 1)
- **Canvas Layout**: Left 2 vertically stacked small images + right 1 large panoramic image. (Pure photo collage).

### Block 4: Three-Column Feature Grid (Row 2, Card 2)
- **Canvas Layout**: 3 equal columns (Image + Title + Description each).

### Block 5: Dual Horizontal Card Layout (Row 3, Card 1)
- **Canvas Layout**: 2 horizontal cards side-by-side (Square image on left + Title & Description stacked on right).

### Block 6: Four-Column Showcase Grid (Row 3, Card 2)
- **Canvas Layout**: 4 equal columns across the row (Image + single caption each).

---

## 5. Image Carousel Workflow (image-carousal-1 to 5)

### Step 1: Open Image Carousel Modal (image-carousal-2)
- **Action**: Click `Image carousel` in the right sidebar under `Insert`.
- **Selector**: `div[role='button']:has-text('Image carousel'), [aria-label*='Image carousel' i]`

### Step 2: Add Images Via `+` Button (image-carousal-1)
- **Action**: In the "Insert images" dialog, click the centered `+` circle icon.
- **Menu Options**:
  - `Upload image` (Local files from computer)
  - `Select image` (From Google Drive)
- **Rule**: Minimum 2 images required.

### Step 3: Multi-Image Thumbnail Gallery (image-carousal-3)
- **Action**: Uploaded images appear as a grid of thumbnails inside the modal.
- **Confirmation**: Blue `Insert` button at bottom-right activates. Click `Insert`.

### Step 4: Canvas Placement & Indicator Dots (image-carousal-4)
- **Result**: Slider carousel lands on canvas, taking up approx 4-5 columns by default.
- **Visual Features**: Navigation pagination dots (`...`) appear centered beneath the active slide.
- **Floating Toolbar**: Settings gear icon, duplicate, delete.

### Step 5: Full-Width Stretch Across 12 Columns (image-carousal-5)
- **Action**: Drag the right edge / bottom-right circle handle horizontally to the 12th rightmost column line.
- **Result**: Image carousel stretches cleanly from edge to edge across the full width of the container.
- **Deselect**: Press `Escape` to remove selection handles and finalize the clean full-width slider view.

---

## 6. Button Component Workflow (Button-1 to 5)

### Step 1: Open Button Modal (Button-1)
- **Action**: Click `Button` under `Insert` tab on the right sidebar.
- **Selector**: `div[role='button']:has-text('Button'), [aria-label*='Button' i]`

### Step 2: Configure Name & Link (Button-2)
- **Modal Title**: "Insert button"
- **Fields**:
  1. `Name` input (`input[type='text']:nth-child(1)`): Button label text (e.g. 'Call Now', 'Book Now', 'Hello World', max 120 characters).
  2. `Link` input (`input[type='text']:nth-child(2)`): Target destination (e.g. `tel:+919876543210`, `https://wa.me/...`, or any external web link).
- **Confirmation**: Click blue `Insert` button (`button:has-text('Insert')`).

### Step 3: Canvas Default Placement (Button-3)
- **Result**: Button lands on canvas as a compact button (~2-3 columns wide).
- **Floating Toolbar**:
  - Style dropdown: `Filled` (solid background), `Outlined`, or `Text`.
  - Alignment: Align Left / Center / Right.
  - Edit (Pencil), Duplicate, Delete (Trash).
- **Selection State**: Blue bounding box with left and right circular dot handles.

### Step 4: Dragging to Full Width (Button-4)
- **Action**: Grab the right-edge blue circle handle and drag horizontally.
- **Behavior**: The 12-column layout grid lines automatically reveal themselves across the canvas.
- **Target**: Drag all the way to the 12th rightmost column boundary line.

### Step 5: Full-Width Button Banner View (Button-5)
- **Result**: Button stretches across all 12 columns, transforming into a bold, high-converting full-width CTA bar (e.g. solid filled banner bar with centered text).
- **Deselect**: Press `Escape` or click canvas to remove selection handles and finalize the layout.

---

## 7. Google Maps Embed Workflow (Map-1 to Map-5)

### Step 1: Open Map Modal (Map-1)
- **Action**: In the right sidebar under the `Insert` tab, scroll down past `Calendar` and click the **`Map`** button.
- **Selector**: `div[role='button']:has-text('Map'), [aria-label*='Map' i]`
- **Position**: Located directly below `Calendar` and above `Docs`.

### Step 2: Search Location & Select (Map-2)
- **Modal Title**: "Select a location"
- **Search Input**:
  - Placeholder: `Search Google Maps`
  - Selector: `input[placeholder*='Search Google Maps' i], input[type='text']`
- **Action**:
  1. Click into the search input.
  2. Type the location, address, city, or business name (e.g. "Dehradun, Uttarakhand", "New Delhi", etc.).
  3. Press `Enter` to search and position the red pin on the interactive map.
  4. Once rendered, click the blue **`Select`** button at the bottom-right of the modal (`button:has-text('Select')`).

### Step 3: Default Canvas Placement (Map-3)
- **Result**: Interactive Google Map box lands on the canvas.
- **Initial Width**: Defaults to approximately 4 to 5 columns wide.
- **Selection State**: Surrounded by a blue outline with resize handles on borders and corners.
- **Floating Toolbar**: Top-left toolbar includes:
  - `Open in new tab` (External link icon)
  - `Delete` (Trash can icon)

### Step 4: Resizing to Full Width Across 12 Columns (Map-4)
- **Action**: Click and hold the right-edge blue circular resize handle (`div.p6n-wysiwyg-selection-handle-e`).
- **Behavior**: The 12 vertical column grid lines reveal themselves across the canvas.
- **Drag Target**: Drag horizontally across to the 12th rightmost column boundary line.

### Step 5: Final Full-Width Map View (Map-5)
- **Result**: The map expands cleanly edge-to-edge across the entire container width (100% full width).
- **Final Touch**: Press `Escape` or click empty canvas space to remove the blue bounding box and handles, leaving a clean, interactive embedded Google Map ready on the live site.

---

## 8. Header Box & Background Image Workflow (header-1 to header-3)

### Step 1: Header Box Anatomy & Controls (header-1)
- **Header Box**: The top hero banner container spanning full width across the top of the Google Site.
- **Header Title Setting**:
  - Clicking on `Your page title` activates the title input box surrounded by blue outline and resize handles.
  - Floating formatting toolbar docks above:
    - Text Style: Defaults to `Title` (H1)
    - Font Family: (e.g. `Lato - Light`)
    - Font Size: (e.g. `64`)
    - Format options: Bold (`B`), Italic (`I`), Underline (`U`), Text Color (`A`), Link, Alignment, Delete.
- **Header Bottom-Left Toolbar**:
  - Contains two buttons docked on the bottom-left edge:
    1. **`Image ▾`** (Background image control button)
    2. **`Header type`** (Allows switching between Cover, Large banner, Banner, Title only)
  - Left outer margin has Delete icon (Trash can).

### Step 2: Opening Image Dropdown & Uploading (header-2)
- **Action**: Hover over the header banner area and click the **`Image ▾`** button.
- **Selector**: `header div[role='button']:has-text('Image'), div[role='banner'] div[role='button']:has-text('Image'), div[aria-label*='Change image' i]`
- **Dropdown Menu**:
  - `Upload` -> Triggers file chooser to select a local image from computer.
  - `Select` -> Opens Google Drive / Gallery image picker.
- **Automation Handling**:
  - Intercept file chooser using `page.expect_file_chooser()`.
  - Click `Upload` (`div[role='menuitem']:has-text('Upload')`).
  - Pass the local image filepath directly via `file_chooser.set_files(image_path)`.

### Step 3: Final Header with Background Image (header-3)
- **Result**:
  - The uploaded image fills the entire header background cleanly behind the title text.
  - At the bottom-left, the controls update to: `Image ▾`, `Reset` (resets to default background), and `Header type`.
  - At the bottom-right, automatic readability adjustments (stars icon) and anchor image position tool appear.
  - Title text (`H1`) remains clearly legible over the background image.

---

## 9. Dragging Buttons Under Header Title (title-button-1 to title-button-5)

### Core Rule / Constraint:
- Google Sites does **not** allow inserting a button directly inside the Header Box from the right sidebar.
- Any new button inserted from `Insert > Button` always lands initially in the section immediately **below** the Header Box.
- To place CTA button(s) directly underneath the H1 Title inside the Header Banner, the button must be dragged upwards into the header.

### Step 1: Initial Button Insertion Below Header (title-button-1)
- **Action**: Insert button via `Insert > Button` with specified Name and Link.
- **Result**: Button lands in the section directly below the Header Box.
- **Active State**: Surrounded by blue border with style dropdown (`Filled`), alignment, edit, and delete toolbar.

### Step 2: Grabbing & Initiating Drag Towards Header (title-button-2)
- **Action**: Grab the button (by its drag handle or center) using mouse down (`mouse.down`).
- **Drag Motion**: Begin dragging vertically upwards towards the Header Box.
- **Behavior**: As dragging starts, layout grid columns appear across the canvas.

### Step 3: Entering Header Box & Blue Docking Line Trigger (title-button-3)
- **Action**: Continue dragging the button upwards inside the Header Box towards the bottom edge of `Your page title`.
- **Visual Cue**: As the dragged button nears the underside of the title text box, Google Sites displays a prominent **solid blue horizontal line** across the width under the title.
- **Meaning**: This blue line indicates the exact valid snap/dock zone for the button inside the Header Box.

### Step 4: Aligning Over the Blue Docking Line (title-button-4)
- **Action**: Hold the cursor directly over/near the blue line indicator.
- **Snap Ready**: The UI confirms the drop position under the title.

### Step 5: Release & Final Docked Header View (title-button-5)
- **Action**: Release the mouse button (`mouse.up`).
- **Result**:
  - The button snaps cleanly into the Header Box directly underneath `Your page title`.
  - It becomes a integrated hero CTA button (e.g. "Hello World" or "Call Now" / "Book Now").
  - Deselect with `Escape` to leave a clean, professional hero banner.

---

## 10. Footer Section Workflow (Footer-1 to Footer-3)

### Step 1: Hovering at Canvas Bottom & Add Footer Button (Footer-1)
- **Trigger**: Move cursor/scroll to the bottom of the canvas.
- **Visual Cue**: A centered pill button **`(+) Add Footer`** appears at the bottom boundary of the page.
- **Selector**: `div[role='button']:has-text('Add footer'), button:has-text('Add footer'), [aria-label*='Add footer' i]`

### Step 2: Footer Input Box & Formatting Toolbar (Footer-2)
- **Action**: Click the `(+) Add Footer` button.
- **Result**:
  - A full-width editable text box container opens in the dedicated footer section.
  - Floating formatting toolbar docks above:
    - Text Style: Defaults to `Small text`
    - Font Family: (e.g. `Lato`)
    - Font Size: (e.g. `9`)
    - Format options: Bold, Italic, Underline, Text Color, Link, Alignment, Delete, etc.
- **Typing**: Fill custom copyright, disclaimer, business address, or footer branding text.

### Step 3: Committing & Final Clean Footer View (Footer-3)
- **Save / Deselect**:
  - Click outside onto the canvas or press `Escape`.
- **Result**:
  - A subtle dotted horizontal separator divides the main canvas from the footer area.
  - The footer text is neatly centered or left-aligned at the bottom across all pages on the site.

---

## 11. Theme Selection & Custom Color Workflow (Themes Tab)

### Step 1: Navigating to Themes Tab
- **Action**: In the right sidebar top tab bar, click on **`Themes`** (next to `Insert` and `Pages`).
- **Selector**: `div[role='tab']:has-text('Themes'), [aria-label*='Themes' i]`
- **Sections Shown**:
  1. `CUSTOM`: (Create theme / Import theme) -> **Do NOT touch custom/import.**
  2. `CREATED BY GOOGLE`: Contains Google's official themes.

### Step 2: Selecting Google Official Themes
- **Available Google Themes**:
  - `Simple` (Default site theme)
  - `Aristotle`
  - `Diplomat`
  - `Vision`
  - `Level`
  - `Impression`
- **Action**: Click the target theme card under `CREATED BY GOOGLE`.
- **Behavior**: The site typography, banner styling, and accent colors update instantly. The core content insertion workflow remains identical.

### Step 3: Color Palette & Custom Hex Color Setting
- **Theme Color Palette**:
  - Directly beneath the selected active theme card, 6 color circles appear:
    - Circles 1 to 5: Pre-set theme color swatches.
    - **Circle 6 (Paint bucket icon / Color point)**: Custom color trigger.
- **Custom Color Setting**:
  - Click the 6th color circle (`div[aria-label*='custom color' i]`, `div[role='button'][style*='background']`).
  - An inline color picker spectrum with Hex input box opens (`input[aria-label*='hex' i]`, `input[value*='#']`).
  - Enter the custom Hex code (e.g. `#800020`).
  - Press `Enter` or click outside to confirm.
- **Default Handling**:
  - If no custom color is specified, the theme's built-in default color is preserved.
  - If `Simple` theme is chosen without custom color, no theme actions are needed (zero overhead).

### Step 4: Return to Insert Tab
- **Action**: Click back to the **`Insert`** tab (`div[role='tab']:has-text('Insert')`) so standard element additions continue seamlessly.

---

## 12. Publishing Workflow & Live URL Extraction (publish-1 to publish-5)

### Step 1: Triggering Publish (publish-1)
- **Action**: Click the solid blue **`Publish`** button in the top-right header toolbar.
- **Selector**: `div[role='button']:has-text('Publish'), button:has-text('Publish')`

### Step 2: 'Publish to the web' Modal & Slug Validation (publish-2)
- **Modal Title**: "Publish to the web"
- **Web Address Input Rules**:
  1. **Strict Lowercase**: Input slug must only contain lowercase alphanumeric characters and hyphens (e.g. `pest-control-mumbai-09101234`).
  2. **Wait 1.5 - 2 Seconds**: After typing into `Web address`, Google Sites performs an asynchronous availability lookup on Google servers. The blue `Publish` button remains disabled during this lookup and only becomes clickable after 1-2 seconds.
  3. **Duplicate Address Handling**: If "already taken" or "already exists" error text appears beneath the input, the automation automatically appends an updated numeric/random suffix and retries until a unique valid address is verified.
  4. **Search Settings Checkbox**: "Request public search engines to not display my site" must **remain UNCHECKED**.
- **Action**: Once the address is accepted and the `Publish` button becomes clickable/enabled, click `Publish`.

### Step 3: Toast Notification & View Link (publish-3)
- **Toast Message**: At the bottom of the screen, a dark toast notification appears:
  `"Your site has been published successfully"` with a **`View`** action button.
- **Selector**: `div:has-text('Your site has been published successfully') a:has-text('View'), div:has-text('Your site has been published successfully') button:has-text('View')`

### Step 4: Extracting URL from New Tab (publish-4)
- **Action**: Clicking **`View`** opens the live site in a new browser tab.
- **Extraction**: The exact live URL (e.g. `https://sites.google.com/view/{slug}/home`) is copied directly from the new tab's address bar and saved to `urls/published_urls.txt`.
- **Cleanup**: The newly opened tab is closed after extracting the URL.

### Step 5: Fallback URL Extraction via 'Copy published site link' (publish-5)
- **Fallback Trigger**: If the bottom toast disappears too quickly or is not caught:
  1. Click the **chain-link icon** in the top header toolbar (`div[role='button'][aria-label*='Copy published site link' i]`).
  2. A modal titled **"Published site link"** opens containing the live URL and a blue **`Copy link`** button.
  3. Extract the URL directly from the modal input field or copy to clipboard.
  4. Save the verified URL to `urls/published_urls.txt`.

---

## 13. Announcement Banner Workflow (announcement-banner-1 to announcement-banner-6)

### Step 1: Open Site Settings (announcement-banner-1)
- **Action**: In the top header toolbar to the left of `Publish`, click the **Settings (Gear) icon**.
- **Selector**: `div[role='button'][aria-label*='Settings' i], button[aria-label*='Settings' i]`
- **Result**: Modal titled "Settings" opens with left-hand category tabs.

### Step 2: Navigate to Announcement Banner & Enable Toggle (announcement-banner-2)
- **Action**: In the left sidebar of the Settings modal, click on **`Announcement banner`**.
- **Selector**: `div[role='tab']:has-text('Announcement banner'), [aria-label*='Announcement banner' i]`
- **Show Banner Toggle**:
  - The right pane displays `Show banner` toggle switch.
  - Action: Ensure toggle is switched ON (`role='switch'`, `aria-checked='true'`).

### Step 2.1: Banner Color Palette & Default Red (announcement-banner-5)
- **Banner Color Trigger**:
  - Right beneath `Show banner`, locate `Banner color` row with current color swatch circle button.
  - **Selector**: `div[role='dialog'] [aria-label*='Banner color' i], div[role='dialog'] div:has-text('Banner color') + div [role='button']`
  - Clicking this button opens the color palette popover.
- **Default Red Selection**:
  - By default, the Banner Color is set to **Red** (Row 2, Column 1 in standard palette).
  - Red circle indicator shows a checkmark when active.
  - If default red is desired, click the Red circle or keep it selected.
- **Custom Color `+` Button**:
  - At the very bottom of the palette grid, there is a round `+` button (`aria-label*='Custom' i` or `aria-label*='Add' i`).
  - Clicking `+` transitions to the custom Hex color picker popup (`announcement-banner-6`).

### Step 2.2: Custom Hex Color Input (announcement-banner-6)
- **Custom Color Popover**:
  - Opens on clicking `+` from the palette grid.
  - Displays color gradient picker, rainbow hue slider, and an inline Hex input field.
- **Hex Input**:
  - **Selector**: `div[role='dialog'] input[aria-label*='Hex' i], input[type='text']:visible`
  - Fill custom hex code (e.g. `#800020`, `#1E3A8A`, etc.).
  - Press `Enter` or click outside to confirm.
- **Result**: Banner background preview dynamically reflects the custom selected color.

### Step 3: Message Field & CTA Content (announcement-banner-3)
- **Message Field**:
  - Located under `Announcement` section.
  - Textarea (`0 / 150` characters) for short, compelling CTA text (e.g., "Instant 24/7 Service Available - Chat on WhatsApp").
  - **Selector**: `div[role='dialog'] textarea, div[role='dialog'] input[aria-label*='Message' i]`

### Step 4: Button Label, Link & Default Settings (announcement-banner-3)
- **Scroll Down**: Scroll down the right pane to reveal button inputs.
- **Fields**:
  1. **Button label** (`input[aria-label*='Button label' i]`): CTA button text (e.g. "WhatsApp", "Chat Now", max 25 chars).
  2. **Link** (`input[aria-label*='Link' i]`): Target destination (e.g. WhatsApp direct link `https://wa.me/...` or phone link).
- **Default Untouched Settings**:
  - `Open in new tab` checkbox: Keep as-is.
  - `Visibility`: Defaults to `All pages` (Keep selected as-is).

### Step 5: Autosave & Final Top Banner View (announcement-banner-4)
- **Close / Save**:
  - Google Sites autosaves announcement banner changes immediately.
  - Press `Escape` or click the top-right `x` (close) button to dismiss Settings.
- **Result**:
  - A vibrant, sticky top announcement banner bar appears spanning full width across the very top of the site (above the header and site name).
  - Rendered in chosen color (Red by default or custom Hex) with message on the left and CTA button on the right.

---

## 14. Structure 1 Specification: 35-Block High-Authority SEO Page Architecture

### Core Rules:
1. **Hero Title as Site Name**: The AI-generated H1 title in the Hero banner is directly used as the `site_name` in document title and header logo text.
2. **Hero WhatsApp Button**: Button labeled `"WHATSAPP"` (link `https://wa.me/...`) is docked directly under the H1 title in the header via the `title-button` drag-and-drop rule.
3. **Theme Color H2 Sections**: Every H2 heading is placed in its own standalone Text Box with **Style 3 (Theme Color)** background applied via the left section color handle.
4. **Option B (Stacked Images + Normal Text)**: Every even section from 2 to 14 includes a full-width uploaded image (from `images/str-image1/`) stacked above its normal text box.
5. **Full-Width Call Buttons**: Blocks 4 and 33 feature `"Call Now"` buttons stretched to 12 columns (full width).
6. **Bulk Keywords**: Block 34 provides a comprehensive comma-separated SEO keyword block.
7. **Google Maps Embed**: Block 35 embeds an interactive Google Map for the target locality, stretched full-width.

### 35-Block Complete Layout Sequence:
- **Block 1**: Hero Section (Full Width Bg Image + H1 Title + 'WHATSAPP' CTA Button in Header)
- **Block 2**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 3**: Text Box – Normal Text (2 paragraphs, ~150 words)
- **Block 4**: Button – Full Width: 'Call Now' (`tel:+...`)
- **Block 5**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 6**: Image Upload + Normal Text (Option B: Stacked Image + 2 paragraphs)
- **Block 7**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 8**: Text Box – Normal Text (3 paragraphs)
- **Block 9**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 10**: Image Upload + Normal Text (Stacked Image + 3 paragraphs)
- **Block 11**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 12**: Text Box – Normal Text (4 paragraphs)
- **Block 13**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 14**: Image Upload + Normal Text (Stacked Image + 3 paragraphs)
- **Block 15**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 16**: Text Box – Normal Text (3 paragraphs)
- **Block 17**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 18**: Image Upload + Normal Text (Stacked Image + 3 paragraphs)
- **Block 19**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 20**: Text Box – Normal Text (3 paragraphs)
- **Block 21**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 22**: Image Upload + Normal Text (Stacked Image + 4 paragraphs)
- **Block 23**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 24**: Text Box – Normal Text (3 paragraphs)
- **Block 25**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 26**: Image Upload + Normal Text (Stacked Image + 3 paragraphs)
- **Block 27**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 28**: Text Box – Normal Text (3 paragraphs)
- **Block 29**: Text Box – H2 Heading (Theme Color Style 3)
- **Block 30**: Image Upload + Normal Text (Stacked Image + 3 paragraphs)
- **Block 31**: Text Box – Final H2 Heading (Theme Color Style 3)
- **Block 32**: Text Box – Normal Text (4 paragraphs)
- **Block 33**: Button – Full Width: 'Call Now' (`tel:+...`)
- **Block 34**: Text Box – Bulk Keywords Box
- **Block 35**: Map: Google Maps Embed (Full Width)









