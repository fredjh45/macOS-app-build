"""
Location and Tag Keywords Helper
Extracts accurate city/locality from target keywords and generates comprehensive 60-80+ SEO tag keywords.
"""

import re
from typing import Tuple, List, Optional

# Comprehensive list of major Indian cities, union territories, states, and prominent localities
KNOWN_LOCATIONS = [
    # Metros & Tier 1/2
    "Delhi", "New Delhi", "South Delhi", "North Delhi", "West Delhi", "East Delhi", "Central Delhi",
    "Noida", "Greater Noida", "Gurgaon", "Gurugram", "Faridabad", "Ghaziabad",
    "Mumbai", "Navi Mumbai", "Thane", "Kalyan", "Andheri", "Bandra", "Colaba", "Juhu",
    "Bangalore", "Bengaluru", "Whitefield", "Koramangala", "Indiranagar", "HSR Layout",
    "Kolkata", "Howrah", "Salt Lake",
    "Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli",
    "Hyderabad", "Secunderabad", "Gachibowli", "Hitec City", "Banjara Hills",
    "Pune", "Pimpri Chinchwad", "Viman Nagar", "Kothrud", "Hinjewadi",
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Gandhinagar",
    "Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner",
    "Lucknow", "Kanpur", "Varanasi", "Agra", "Prayagraj", "Allahabad", "Meerut", "Bareilly", "Aligarh", "Gorakhpur", "Moradabad", "Jhansi",
    "Chandigarh", "Mohali", "Panchkula", "Ludhiana", "Amritsar", "Jalandhar",
    "Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain",
    "Patna", "Gaya", "Muzaffarpur", "Bhagalpur",
    "Ranchi", "Jamshedpur", "Dhanbad",
    "Bhubaneswar", "Cuttack", "Rourkela",
    "Raipur", "Bhilai", "Bilaspur",
    "Dehradun", "Haridwar", "Rishikesh", "Roorkee", "Nainital",
    "Shimla", "Manali", "Dharamshala",
    "Goa", "Panaji", "Margao", "Calangute", "Candolim", "Baga",
    "Guwahati", "Siliguri", "Shillong",
    "Kochi", "Cochin", "Thiruvananthapuram", "Trivandrum", "Kozhikode",
    "Vijayawada", "Visakhapatnam", "Vizag", "Guntur", "Nellore", "Tirupati",
    "Nagpur", "Nashik", "Aurangabad", "Solapur", "Kolhapur", "Amravati",
    "Jammu", "Srinagar",
    # Prominent Delhi NCR Localities
    "Aerocity", "Mahipalpur", "Rohini", "Dwarka", "Janakpuri", "Karol Bagh", "Connaught Place",
    "Saket", "Hauz Khas", "Vasant Kunj", "Lajpat Nagar", "Pitampura", "Paschim Vihar", "Paharganj"
]

# Build regex pattern for case-insensitive exact word boundary matching of known locations
_SORTED_LOCATIONS = sorted(KNOWN_LOCATIONS, key=len, reverse=True)
_LOCATION_REGEX = re.compile(
    r'\b(' + '|'.join(re.escape(loc) for loc in _SORTED_LOCATIONS) + r')\b',
    re.IGNORECASE
)


def extract_location_and_map_query(keyword: str) -> Tuple[str, str]:
    """
    Extracts the most accurate city/locality and Google Maps query from a keyword.
    
    Returns:
        (city_name, map_query)
        e.g. ("Delhi", "New Delhi, Delhi, India")
             ("Mumbai", "Mumbai, Maharashtra, India")
             ("Jaipur", "Jaipur, Rajasthan, India")
    """
    if not keyword or not keyword.strip():
        return ("Delhi", "New Delhi, Delhi, India")

    kw = keyword.strip()

    # 1. Match against known locations list (highest accuracy)
    loc_match = _LOCATION_REGEX.search(kw)
    if loc_match:
        matched_name = loc_match.group(1)
        for known in _SORTED_LOCATIONS:
            if known.lower() == matched_name.lower():
                city = known
                break
        else:
            city = matched_name.title()

        if city.lower() == "goa":
            map_query = "Goa, India"
        elif city.lower() in ["delhi", "new delhi"]:
            map_query = "New Delhi, Delhi, India"
        elif city.lower() in ["aerocity", "mahipalpur", "rohini", "dwarka", "saket", "karol bagh", "connaught place", "vasant kunj", "hauz khas"]:
            map_query = f"{city}, New Delhi, India"
        elif city.lower() in ["noida", "greater noida"]:
            map_query = f"{city}, Uttar Pradesh, India"
        elif city.lower() in ["gurgaon", "gurugram", "faridabad"]:
            map_query = f"{city}, Haryana, India"
        elif city.lower() in ["mumbai", "navi mumbai", "thane", "pune"]:
            map_query = f"{city}, Maharashtra, India"
        elif city.lower() in ["bangalore", "bengaluru"]:
            map_query = "Bengaluru, Karnataka, India"
        elif city.lower() in ["jaipur", "jodhpur", "udaipur"]:
            map_query = f"{city}, Rajasthan, India"
        elif city.lower() in ["dehradun", "haridwar", "rishikesh"]:
            map_query = f"{city}, Uttarakhand, India"
        else:
            map_query = f"{city}, India"
        return (city, map_query)

    # 2. Heuristic extraction: "in <City>" or "near <City>" or "at <City>"
    prep_match = re.search(r'\b(?:in|near|at)\s+([A-Za-z\s]{2,25})', kw, re.IGNORECASE)
    if prep_match:
        candidate = prep_match.group(1).strip()
        candidate = re.sub(r'\b(?:service|agency|call\s+girl|escort|hotel|center|centre|pest\s+control)\b.*$', '', candidate, flags=re.IGNORECASE).strip()
        if candidate and len(candidate) >= 3:
            city = candidate.title()
            return (city, f"{city}, India")

    # 3. Fallback: use cleaned keyword title (NEVER default to Dehradun!)
    cleaned_kw = re.sub(r'\s+', ' ', kw).strip().title()
    return (cleaned_kw, f"{cleaned_kw}, India")


def generate_comprehensive_tag_keywords(
    keyword: str,
    city: str,
    related_keywords: Optional[List[str]] = None
) -> str:
    """
    Generates an abundant, high-density list of 60 to 80+ unique, relevant long-tail SEO tag keywords.
    Ensures that every published post has extensive keyword coverage.
    """
    kw_title = keyword.strip().title()
    city_title = city.strip().title() if city else "Delhi"

    tags = []

    # 1. Primary & User-Supplied Keywords (if any)
    tags.append(kw_title)
    tags.append(f"{kw_title} {city_title}")
    tags.append(f"{kw_title} in {city_title}")

    if related_keywords:
        for rk in related_keywords:
            rk_clean = rk.strip().title()
            if rk_clean and rk_clean not in tags:
                tags.append(rk_clean)

    # 2. "Near Me" and Proximity Queries
    proximity_templates = [
        f"{kw_title} Near Me",
        f"Best {kw_title} Near Me",
        f"Top Rated {kw_title} Near Me",
        f"Verified {kw_title} Near Me",
        f"24/7 {kw_title} Near Me",
        f"Doorstep {kw_title} Near Me",
        f"Affordable {kw_title} Near Me",
        f"Local {kw_title} Near Me",
        f"Immediate {kw_title} Near Me",
        f"Cheap Rate {kw_title} Near Me"
    ]
    for t in proximity_templates:
        if t not in tags:
            tags.append(t)

    # 3. City-Specific Authority & Search Intent
    city_templates = [
        f"Best {kw_title} in {city_title}",
        f"Top {kw_title} in {city_title}",
        f"Affordable {kw_title} in {city_title}",
        f"Verified {kw_title} in {city_title}",
        f"Genuine {kw_title} in {city_title}",
        f"Independent {kw_title} in {city_title}",
        f"VIP {kw_title} in {city_title}",
        f"High Profile {kw_title} in {city_title}",
        f"Low Rate {kw_title} in {city_title}",
        f"Cheap Price {kw_title} in {city_title}",
        f"24 Hours {kw_title} in {city_title}",
        f"Doorstep {kw_title} in {city_title}",
        f"Hotel Delivery {kw_title} in {city_title}",
        f"Direct Cash Payment {kw_title} in {city_title}",
        f"No Advance Payment {kw_title} in {city_title}",
        f"{city_title} {kw_title} Agency",
        f"{city_title} {kw_title} Service",
        f"{city_title} {kw_title} Price List",
        f"{city_title} {kw_title} Rates",
        f"{city_title} {kw_title} Contact Number",
        f"{city_title} {kw_title} WhatsApp Number",
        f"{city_title} Real {kw_title} Phone Number",
        f"{city_title} Local {kw_title} Profiles",
        f"Certified {kw_title} in {city_title}",
        f"Popular {kw_title} in {city_title}"
    ]
    for t in city_templates:
        if t not in tags:
            tags.append(t)

    # 4. Actionable Transactional & Contact Modifiers
    action_templates = [
        f"{kw_title} Contact Details",
        f"{kw_title} WhatsApp Booking",
        f"{kw_title} Online Booking",
        f"{kw_title} Direct Call Booking",
        f"{kw_title} Cash on Delivery",
        f"{kw_title} Without Advance",
        f"{kw_title} 100% Safe & Secure",
        f"{kw_title} Real Photos",
        f"{kw_title} Genuine Agency",
        f"Top Rated Agency for {kw_title}",
        f"Fast 20 Mins Arrival {kw_title}",
        f"Emergency 24/7 {kw_title}",
        f"Late Night {kw_title} Service",
        f"Full Night {kw_title} Packages",
        f"Short Duration {kw_title} Rates",
        f"Budget Friendly {kw_title} Service",
        f"Exclusive VIP {kw_title} Deals",
        f"5-Star Rated {kw_title} Provider",
        f"Trusted Service Desk {kw_title}",
        f"Instant Response WhatsApp {kw_title}",
        f"Verified Local {kw_title}",
        f"Premium Companions {kw_title}",
        f"Discreet Doorstep {kw_title}",
        f"Top Agency in {city_title} for {kw_title}",
        f"Lowest Price Guaranteed {kw_title}",
        f"Genuine Client Reviews {kw_title}",
        f"24/7 Available {kw_title} Helpline"
    ]
    for t in action_templates:
        if t not in tags:
            tags.append(t)

    # 5. Hinglish & Local Search Terms (High Search Volume)
    hinglish_templates = [
        f"{kw_title} कॉल और व्हाट्सएप्प नंबर",
        f"{kw_title} 24 घंटे सेवा उपलब्ध",
        f"{kw_title} बेस्ट रेट और डिस्काउंट",
        f"{city_title} में {kw_title} की सर्विस",
        f"{city_title} {kw_title} बिना एडवांस पेमेंट"
    ]
    for t in hinglish_templates:
        if t not in tags:
            tags.append(t)

    # Deduplicate while preserving order and limit to 75
    unique_tags = []
    seen = set()
    for item in tags:
        clean = item.strip()
        if clean and clean.lower() not in seen:
            seen.add(clean.lower())
            unique_tags.append(clean)
        if len(unique_tags) >= 75:
            break

    return ", ".join(unique_tags)
