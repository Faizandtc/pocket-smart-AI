import json
import base64
import os
import httpx
from typing import Dict, Any, Optional
from app.config import GEMINI_API_KEY

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

async def call_gemini_api(prompt: str, image_bytes: Optional[bytes] = None, mime_type: str = "image/jpeg", user_api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Calls Gemini API with prompt and optional image. Returns parsed JSON or None if failed.
    """
    api_key = user_api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    url = f"{GEMINI_API_URL}?key={api_key}"
    
    parts = []
    if image_bytes:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded_image
            }
        })
    
    parts.append({"text": prompt})
    
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
            else:
                print(f"Gemini API returned status {response.status_code}: {response.text}")
                return None
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None


# -------------------------------------------------------------
# 1. HOME INTERIOR PLANNER GENERATOR
# -------------------------------------------------------------
async def generate_interior_plan(
    room_type: str,
    style: str,
    dimensions: str,
    budget: float,
    currency: str = "$",
    special_requirements: str = "",
    target_palette: str = "Warm Neutrals & Accents",
    user_api_key: Optional[str] = None
) -> Dict[str, Any]:
    
    prompt = f"""
    You are an elite interior architect and financial lifestyle planner. Create a comprehensive, realistic budget-based interior design recommendation plan in strict JSON.
    Room: {room_type}
    Style: {style}
    Dimensions: {dimensions}
    Total Budget: {currency}{budget:,.2f}
    Special Requirements: {special_requirements or 'None'}
    Target Palette: {target_palette}

    Return a JSON object with this exact structure:
    {{
      "title": "Creative title for this room design",
      "summary": "Detailed narrative explaining the design concept and how budget was maximized",
      "color_palette": [
        {{"name": "Color Name", "hex": "#HEX", "role": "Base / Secondary / Accent / Neutral", "rationale": "Why this shade"}}
      ],
      "budget_breakdown": [
        {{
          "category": "Furniture / Lighting / Soft Furnishings / Wall Decor & Art / Greenery & Accents / Tools & Hardware",
          "percentage": 40,
          "allocated_amount": 400.00,
          "items": [
            {{"name": "Item Name", "est_cost": 250.00, "priority": "Must-Have", "shopping_tip": "Specific sourcing or material advice"}}
          ]
        }}
      ],
      "tiers": {{
        "thrifty": {{"label": "Thrifty Saver", "total": 0.8 * budget, "strategy": "DIY + IKEA/Marketplace finds", "key_choices": ["...", "..."]}},
        "balanced": {{"label": "Balanced Design", "total": budget, "strategy": "High-low mix with durable focal pieces", "key_choices": ["...", "..."]}},
        "luxe": {{"label": "Luxe Upgrade", "total": 1.25 * budget, "strategy": "Custom upholstery and designer lighting", "key_choices": ["...", "..."]}}
      }},
      "spatial_advice": ["Tip 1 on placement", "Tip 2 on traffic flow", "Tip 3 on vertical height"],
      "cost_saving_hacks": ["Clever hack 1", "Clever hack 2", "Clever hack 3"],
      "total_allocated": {budget}
    }}
    """
    
    gemini_result = await call_gemini_api(prompt, user_api_key=user_api_key)
    if gemini_result and "budget_breakdown" in gemini_result:
        return gemini_result

    # High-fidelity domain-expert fallback generator
    return get_fallback_interior_plan(room_type, style, dimensions, budget, currency, special_requirements, target_palette)


def get_fallback_interior_plan(
    room_type: str, style: str, dimensions: str, budget: float, currency: str, special_requirements: str, target_palette: str
) -> Dict[str, Any]:
    # Style Palettes Mapping
    palette_map = {
        "Scandinavian": [
            {"name": "Birch Snow", "hex": "#F8F9FA", "role": "Base Walls", "rationale": "Reflects natural light and expands visual space"},
            {"name": "Nordic Slate", "hex": "#4A5568", "role": "Secondary", "rationale": "Grounded contrast for anchor furniture"},
            {"name": "Sage Moss", "hex": "#84A98C", "role": "Botanical Accent", "rationale": "Calming biophilic warmth"},
            {"name": "Blonde Oak", "hex": "#D4A373", "role": "Natural Wood", "rationale": "Warm organic texture to offset minimalist lines"}
        ],
        "Modern Minimalist": [
            {"name": "Chantilly White", "hex": "#FDFBF7", "role": "Base Walls", "rationale": "Clean, crisp backdrop without clinical glare"},
            {"name": "Matte Charcoal", "hex": "#2B2D42", "role": "Architectural Accent", "rationale": "Sharp silhouettes and window trims"},
            {"name": "Warm Greige", "hex": "#B7B59F", "role": "Secondary Neutral", "rationale": "Softens the transition between light and dark"},
            {"name": "Brushed Brass", "hex": "#C5A059", "role": "Metallic Pop", "rationale": "Upscale metallic warmth in hardware and fixtures"}
        ],
        "Japandi": [
            {"name": "Raw Linen", "hex": "#EAE5D9", "role": "Base Tone", "rationale": "Earthy, unbleached serenity"},
            {"name": "Cedar Timber", "hex": "#8C6D58", "role": "Mid-Tone Wood", "rationale": "Handcrafted Japanese joinery feel"},
            {"name": "Wabi Sabi Black", "hex": "#1F2421", "role": "Minimal Contrast", "rationale": "Ink-wash grounding accents"},
            {"name": "Clay Terracotta", "hex": "#C17C64", "role": "Organic Accent", "rationale": "Earthy pottery warmth"}
        ],
        "Bohemian": [
            {"name": "Warm Sand", "hex": "#EFE6DD", "role": "Base Layer", "rationale": "Neutral canvas allowing colorful textiles to shine"},
            {"name": "Terracotta Rust", "hex": "#BC6C25", "role": "Primary Color", "rationale": "Earthy warmth on rugs and cushions"},
            {"name": "Deep Ochre", "hex": "#DDA15E", "role": "Secondary Pop", "rationale": "Sun-drenched warmth in throws and art"},
            {"name": "Forest Fern", "hex": "#283618", "role": "Accent Green", "rationale": "Rich leafy contrast for potted plants"}
        ],
        "Industrial Luxe": [
            {"name": "Exposed Concrete", "hex": "#9AA0A6", "role": "Base Texture", "rationale": "Urban loft industrial foundation"},
            {"name": "Cognac Leather", "hex": "#9E5A38", "role": "Statement Texture", "rationale": "Rich vintage warmth to balance cold metal"},
            {"name": "Blackened Steel", "hex": "#1A1A1D", "role": "Structural Accents", "rationale": "Iron pipe legs, track lighting, and frames"},
            {"name": "Amber Edison", "hex": "#E09F3E", "role": "Luminous Warmth", "rationale": "Golden ambient glow softening industrial edges"}
        ]
    }
    
    palette = palette_map.get(style, palette_map["Modern Minimalist"])

    # Dynamic Allocation ratios
    furniture_share = 0.46
    lighting_share = 0.16
    textiles_share = 0.16
    decor_share = 0.14
    contingency_share = 0.08

    furn_alloc = round(budget * furniture_share, 2)
    light_alloc = round(budget * lighting_share, 2)
    text_alloc = round(budget * textiles_share, 2)
    decor_alloc = round(budget * decor_share, 2)
    cont_alloc = round(budget * contingency_share, 2)

    # Dynamic room-specific items
    is_bedroom = "bedroom" in room_type.lower()
    is_office = "office" in room_type.lower()
    
    if is_bedroom:
        main_furniture = [
            {"name": f"{style} Upholstered Platform Bed Frame", "est_cost": round(furn_alloc * 0.52, 2), "priority": "Must-Have", "shopping_tip": "Look for hardwood slat support with integrated headboard padding"},
            {"name": "Pair of Floating / Minimalist Nightstands", "est_cost": round(furn_alloc * 0.28, 2), "priority": "Recommended", "shopping_tip": "Keep floor clearance visible to make room appear larger"},
            {"name": "Storage Dresser or Wardrobe Organizer", "est_cost": round(furn_alloc * 0.20, 2), "priority": "Must-Have", "shopping_tip": "Flat-pack with upgraded brushed hardware pulls"}
        ]
        textiles = [
            {"name": "100% Washed Linen / Percale Duvet & Pillow Set", "est_cost": round(text_alloc * 0.45, 2), "priority": "Must-Have", "shopping_tip": "Breathable all-season natural fibers"},
            {"name": "Large Low-Pile Area Rug (8x10)", "est_cost": round(text_alloc * 0.40, 2), "priority": "Must-Have", "shopping_tip": "Position 2/3 under bed extending 2 feet on sides"},
            {"name": "Thermal Blackout Linen Drapery", "est_cost": round(text_alloc * 0.15, 2), "priority": "Recommended", "shopping_tip": "Mount curtain rods 4-6 inches above window frame to heighten ceiling"}
        ]
    elif is_office:
        main_furniture = [
            {"name": f"Ergonomic Standing/Seated Desk ({style})", "est_cost": round(furn_alloc * 0.50, 2), "priority": "Must-Have", "shopping_tip": "Dual motor with cable management grommets"},
            {"name": "High-Back Breathable Ergonomic Mesh/Leather Chair", "est_cost": round(furn_alloc * 0.35, 2), "priority": "Must-Have", "shopping_tip": "Prioritize adjustable lumbar and armrests"},
            {"name": "Modular Bookshelf & Storage Credenza", "est_cost": round(furn_alloc * 0.15, 2), "priority": "Recommended", "shopping_tip": "Keep visual clutter concealed behind lower cabinet doors"}
        ]
        textiles = [
            {"name": "Sound-Dampening Geometric Wool Blend Rug", "est_cost": round(text_alloc * 0.65, 2), "priority": "Must-Have", "shopping_tip": "Reduces call echo while protecting flooring under wheels"},
            {"name": "Textured Lumbar Pillow & Throw", "est_cost": round(text_alloc * 0.35, 2), "priority": "Recommended", "shopping_tip": "Adds warmth and ergonomic support for long work sessions"}
        ]
    else:  # Living room or general
        main_furniture = [
            {"name": f"{style} Performance Fabric Sofa (3-Seater / Sectional)", "est_cost": round(furn_alloc * 0.60, 2), "priority": "Must-Have", "shopping_tip": "Choose stain-resistant performance weave with high-density foam cushions"},
            {"name": "Fluted Wood / Glass Top Nested Coffee Table", "est_cost": round(furn_alloc * 0.22, 2), "priority": "Recommended", "shopping_tip": "Nesting tables offer flexible space when hosting guests"},
            {"name": "Sculptural Accent Lounge Armchair", "est_cost": round(furn_alloc * 0.18, 2), "priority": "Recommended", "shopping_tip": "Contrasting texture (bouclé or warm leather) anchors the corner"}
        ]
        textiles = [
            {"name": "Oversized Textured Area Rug (8x10)", "est_cost": round(text_alloc * 0.55, 2), "priority": "Must-Have", "shopping_tip": "All front legs of seating should rest on the rug"},
            {"name": "Curated Cushion Trio & Woven Throw Blanket", "est_cost": round(text_alloc * 0.25, 2), "priority": "Recommended", "shopping_tip": "Mix sizes: two 20x20 solids, one 14x20 patterned lumbar"},
            {"name": "Light Filtering Sheer Linen Curtains", "est_cost": round(text_alloc * 0.20, 2), "priority": "Recommended", "shopping_tip": "Floor-to-ceiling pinch pleat for designer hotel aesthetic"}
        ]

    lighting_items = [
        {"name": f"{style} Statement Pendant / Chandelier", "est_cost": round(light_alloc * 0.55, 2), "priority": "Must-Have", "shopping_tip": "Dimmer-compatible warm white (2700K) centerpiece"},
        {"name": "Arc Floor Lamp or Task Reading Light", "est_cost": round(light_alloc * 0.30, 2), "priority": "Recommended", "shopping_tip": "Creates cozy secondary lighting zone"},
        {"name": "Ceramic Table Lamp with Linen Shade", "est_cost": round(light_alloc * 0.15, 2), "priority": "Optional", "shopping_tip": "Layer light at eye-level"}
    ]

    decor_items = [
        {"name": "Curated Gallery Wall Triptych / Large Canvas Art", "est_cost": round(decor_alloc * 0.45, 2), "priority": "Recommended", "shopping_tip": "Print digital artwork and frame in lightweight gallery frames"},
        {"name": "Indoor Architectural Plant (Fiddle Leaf or Olive Tree) + Ceramic Planter", "est_cost": round(decor_alloc * 0.30, 2), "priority": "Recommended", "shopping_tip": "Brings organic height and vibrancy"},
        {"name": "Sculptural Ceramic Vases, Travertine Tray & Scented Candle", "est_cost": round(decor_alloc * 0.25, 2), "priority": "Optional", "shopping_tip": "Style using the rule of three (varying heights)"}
    ]

    contingency_items = [
        {"name": "Wall Mounts, Felt Floor Pads & Smart Dimmer Switches", "est_cost": round(cont_alloc * 0.50, 2), "priority": "Must-Have", "shopping_tip": "Crucial hardware to prevent floor scratching and hide cords"},
        {"name": "Assembly Buffer / Delivery Cushion", "est_cost": round(cont_alloc * 0.50, 2), "priority": "Recommended", "shopping_tip": "Absorbs unexpected shipping fees or tool rentals"}
    ]

    breakdown = [
        {"category": "Core Furniture", "percentage": 46, "allocated_amount": furn_alloc, "items": main_furniture},
        {"category": "Lighting & Ambiance", "percentage": 16, "allocated_amount": light_alloc, "items": lighting_items},
        {"category": "Textiles & Soft Goods", "percentage": 16, "allocated_amount": text_alloc, "items": textiles},
        {"category": "Decor, Art & Greenery", "percentage": 14, "allocated_amount": decor_alloc, "items": decor_items},
        {"category": "Hardware & Contingency Buffer", "percentage": 8, "allocated_amount": cont_alloc, "items": contingency_items}
    ]

    thrifty_tot = round(budget * 0.78, 2)
    balanced_tot = round(budget, 2)
    luxe_tot = round(budget * 1.30, 2)

    return {
        "title": f"{style} {room_type} Master Plan",
        "summary": f"A cohesive, high-impact design tailored for {dimensions or 'standard dimensions'} in {style} aesthetic. Every dollar of your {currency}{budget:,.2f} budget is strategically distributed to prioritize foundational comfort while crafting an elevated visual sanctuary.",
        "color_palette": palette,
        "budget_breakdown": breakdown,
        "tiers": {
            "thrifty": {
                "label": "Smart Thrifty Saver",
                "total": thrifty_tot,
                "strategy": "Flatpack bases upgraded with custom hardware, marketplace vintage tables, and downloadable printable art frames.",
                "key_choices": [
                    "Sofa from high-rated budget retailer with scotchguard protection",
                    "Printable museum art prints placed in budget IKEA Ribba frames",
                    "DIY upcycled side table with matte spray paint finish"
                ]
            },
            "balanced": {
                "label": "Designer Balanced (Recommended)",
                "total": balanced_tot,
                "strategy": "Investment anchor sofa paired with mid-tier lighting and natural wool/cotton textiles for longevity.",
                "key_choices": [
                    "High-resilience foam sofa with removable washable covers",
                    "Solid oak coffee table and dimmable brass pendant fixture",
                    "100% natural wool/linen blend rug for texture and sound absorption"
                ]
            },
            "luxe": {
                "label": "Luxe Bespoke Tier",
                "total": luxe_tot,
                "strategy": "Solid hardwood joinery, custom-ordered performance velvet, artisan ceramic lighting, and framed original art.",
                "key_choices": [
                    "Custom handcrafted sofa with down-feather blend cushions",
                    "Designer architectural lighting with smart automated dimming",
                    "Bespoke Roman shades and gallery-stretched textured artwork"
                ]
            }
        },
        "spatial_advice": [
            f"Anchor layout around the natural light source in the {dimensions or 'room'}.",
            "Maintain at least 30 to 36 inches of unobstructed walkway space between major furniture pieces.",
            "Use layered lighting: ambient ceiling fixture, task lighting at 4 feet, and warm floor glow at 2 feet."
        ],
        "cost_saving_hacks": [
            "Upgrade budget furniture instantly by replacing factory legs and cabinet handles with solid brushed brass or matte black hardware.",
            "Buy digital museum print files (often open source / $5 on Etsy) and print large format at local photo shops for instant $200+ wall art look.",
            "Choose a large neutral rug and layer a smaller, high-end patterned accent rug on top to save up to 40% on rug costs."
        ],
        "total_allocated": budget
    }


# -------------------------------------------------------------
# 2. PARTY & EVENT PLANNER GENERATOR
# -------------------------------------------------------------
async def generate_party_plan(
    event_type: str,
    guest_count: int,
    theme: str,
    budget: float,
    currency: str = "$",
    venue_type: str = "Indoor Apartment / Home",
    special_notes: str = "",
    user_api_key: Optional[str] = None
) -> Dict[str, Any]:
    
    prompt = f"""
    You are a master event producer and luxury party budget planner. Create an unforgettable event experience plan in strict JSON.
    Event Type: {event_type}
    Guest Count: {guest_count}
    Theme: {theme}
    Total Budget: {currency}{budget:,.2f}
    Per Guest Budget: {currency}{budget / max(1, guest_count):,.2f}
    Venue: {venue_type}
    Notes: {special_notes or 'None'}

    Return a JSON object with this exact structure:
    {{
      "title": "Vibrant party name",
      "per_guest_cost": {round(budget / max(1, guest_count), 2)},
      "summary": "Compelling party concept and how to create maximum vibe on budget",
      "budget_breakdown": [
        {{
          "category": "Catering & Finger Foods / Signature Drinks & Bar / Thematic Decor & Lighting / Music, Sound & Entertainment / Photo Zone & Favors / Clean-up & Contingency",
          "percentage": 35,
          "allocated_amount": 350.00,
          "items": [
            {{"name": "Item Name", "est_cost": 150.00, "priority": "Essential", "tip": "Budget preservation tip"}}
          ]
        }}
      ],
      "tiers": {{
        "thrifty": {{"label": "Budget Smart Host", "total": 0.75 * budget, "strategy": "BYOB mixers + curated charcuterie boards", "key_choices": ["...", "..."]}},
        "balanced": {{"label": "Signature Host (Recommended)", "total": budget, "strategy": "Batch craft cocktails + catering spread", "key_choices": ["...", "..."]}},
        "luxe": {{"label": "VIP Gala Experience", "total": 1.35 * budget, "strategy": "Hired mixologist + live DJ or acoustic set", "key_choices": ["...", "..."]}}
      }},
      "timeline": [
        {{"time": "T - 2 Hours", "action": "Arrival & Ambience Prep", "details": "Chill beverages, set low ambient lighting, queue opening lo-fi playlist"}},
        {{"time": "T + 0:00", "action": "Guest Welcome & Signature Drink", "details": "Hand guests signature cocktail upon entry"}},
        {{"time": "T + 1:15", "action": "Food Spread & Mingling", "details": "Serve hot appetizers, transition playlist to upbeat grooves"}},
        {{"time": "T + 2:30", "action": "Main Event / Toast / Activity", "details": "Themed games, toast, or dance floor activation"}},
        {{"time": "T + 4:00", "action": "Late Night Snacks & Wind-Down", "details": "Sweet treats, warm coffee/tea, parting favor bags"}}
      ],
      "music_and_vibe": {{
        "vibe_description": "Lighting temperature and mood",
        "recommended_genres": ["Genre 1", "Genre 2", "Genre 3"],
        "lighting_setup": "String warm fairy lights + smart color washes"
      }},
      "cost_saving_hacks": ["Hack 1", "Hack 2", "Hack 3"],
      "total_allocated": {budget}
    }}
    """

    gemini_result = await call_gemini_api(prompt, user_api_key=user_api_key)
    if gemini_result and "budget_breakdown" in gemini_result:
        return gemini_result

    return get_fallback_party_plan(event_type, guest_count, theme, budget, currency, venue_type, special_notes)


def get_fallback_party_plan(
    event_type: str, guest_count: int, theme: str, budget: float, currency: str, venue_type: str, special_notes: str
) -> Dict[str, Any]:
    per_guest = round(budget / max(1, guest_count), 2)
    
    # Allocations
    food_share = 0.38
    bar_share = 0.25
    decor_share = 0.17
    entertainment_share = 0.12
    contingency_share = 0.08

    food_alloc = round(budget * food_share, 2)
    bar_alloc = round(budget * bar_share, 2)
    decor_alloc = round(budget * decor_share, 2)
    ent_alloc = round(budget * entertainment_share, 2)
    cont_alloc = round(budget * contingency_share, 2)

    food_items = [
        {"name": f"Artisanal Grazing Table & Charcuterie ({guest_count} Pax)", "est_cost": round(food_alloc * 0.45, 2), "priority": "Essential", "tip": "Cured meats, artisan cheeses, fresh grapes, fig jam, and crusty baguettes look lavish without catering markups"},
        {"name": "Gourmet Hot Sliders & Skewer Bites", "est_cost": round(food_alloc * 0.35, 2), "priority": "Essential", "tip": "Order platters from local bakery or specialty deli rather than full-service caterer"},
        {"name": "Dessert Station / Custom Mini Cupcakes", "est_cost": round(food_alloc * 0.20, 2), "priority": "Recommended", "tip": "Tiered presentation on cake stands creates a high-end bakery aesthetic"}
    ]

    bar_items = [
        {"name": f"Theme Signature Cocktail Batch ('{theme} Sparkler')", "est_cost": round(bar_alloc * 0.45, 2), "priority": "Essential", "tip": "Batch in large beverage dispensers with fresh citrus and herb garnishes (saves 60% vs per-drink mixing)"},
        {"name": "Curated Wine, Prosecco & Craft Beer Selection", "est_cost": round(bar_alloc * 0.35, 2), "priority": "Essential", "tip": "Buy by the case (10-15% discount at warehouse clubs)"},
        {"name": "Artisanal Mocktails, Tonic, Ice & Garnishes", "est_cost": round(bar_alloc * 0.20, 2), "priority": "Recommended", "tip": "Fresh mint, dehydrated lime wheels, and premium club sodas"}
    ]

    decor_items = [
        {"name": f"{theme} Themed Balloon Garland & Backdrop Frame", "est_cost": round(decor_alloc * 0.45, 2), "priority": "Recommended", "tip": "DIY balloon garland kit with electric pump takes 45 mins and saves $250"},
        {"name": "Atmospheric Lighting (LED Uplights / Fairy Lights)", "est_cost": round(decor_alloc * 0.30, 2), "priority": "Essential", "tip": "Dim overhead ceiling lights completely; use warm uplights and candle lanterns"},
        {"name": "Table Runners, Votives & Customized Signage", "est_cost": round(decor_alloc * 0.25, 2), "priority": "Recommended", "tip": "Print Canva templates for drink menus and welcome board"}
    ]

    ent_items = [
        {"name": "Wireless High-Fidelity Bluetooth Speaker Setup", "est_cost": round(ent_alloc * 0.50, 2), "priority": "Essential", "tip": "Pair two portable speakers in stereo mode for 360-degree room sound"},
        {"name": "Interactive Photo Booth Corner (Ring Light + Props)", "est_cost": round(ent_alloc * 0.30, 2), "priority": "Recommended", "tip": "Guests use their own phones with a shared QR code Google Photos album or live Instagram hashtag"},
        {"name": "Curated Spot-on Party Games & Icebreaker Cards", "est_cost": round(ent_alloc * 0.20, 2), "priority": "Optional", "tip": "Creates easy social laughter without forced stiffness"}
    ]

    cont_items = [
        {"name": "Eco-friendly Palm Leaf Plates, Glassware & Napkins", "est_cost": round(cont_alloc * 0.60, 2), "priority": "Essential", "tip": "Heavyweight compostable tableware looks upscale and makes cleanup effortless"},
        {"name": "Contingency Buffer (Extra Ice, Cups, Quick Runs)", "est_cost": round(cont_alloc * 0.40, 2), "priority": "Essential", "tip": "Always keep 5-10% unspent for last-minute ice or beverage replenishment"}
    ]

    breakdown = [
        {"category": "Catering & Gourmet Bites", "percentage": 38, "allocated_amount": food_alloc, "items": food_items},
        {"category": "Signature Bar & Beverages", "percentage": 25, "allocated_amount": bar_alloc, "items": bar_items},
        {"category": "Atmospheric Decor & Lighting", "percentage": 17, "allocated_amount": decor_alloc, "items": decor_items},
        {"category": "Sound, Entertainment & Photo Station", "percentage": 12, "allocated_amount": ent_alloc, "items": ent_items},
        {"category": "Tableware & Contingency Reserve", "percentage": 8, "allocated_amount": cont_alloc, "items": cont_items}
    ]

    return {
        "title": f"The Ultimate {theme} {event_type}",
        "per_guest_cost": per_guest,
        "summary": f"An electrifying, seamlessly choreographed plan for {guest_count} guests celebrating '{theme}' in {venue_type}. Built on a precision budget of {currency}{budget:,.2f} ({currency}{per_guest}/guest) to deliver high sensory impact without overspending on hidden overheads.",
        "budget_breakdown": breakdown,
        "tiers": {
            "thrifty": {
                "label": "Casual Host Edition",
                "total": round(budget * 0.75, 2),
                "strategy": "Potluck dessert integration, batch punch drinks, and digital music queue.",
                "key_choices": [
                    "Host prepares grazing board bases; guests bring specialty beverages",
                    "Canva printed DIY photo booth with phone tripod and ring light",
                    "Curated Spotify DJ crossfade playlist"
                ]
            },
            "balanced": {
                "label": "Signature Host Edition (Recommended)",
                "total": round(budget, 2),
                "strategy": "Fully hosted hot & cold food spread, dual signature cocktail dispensers, and full atmospheric light styling.",
                "key_choices": [
                    "Full artisanal charcuterie and gourmet sliders",
                    "Two signature cocktails + craft beer & wine cases",
                    "Custom balloon backdrop and smart LED ambient wash"
                ]
            },
            "luxe": {
                "label": "VIP Soirée Edition",
                "total": round(budget * 1.35, 2),
                "strategy": "Hired mixologist for 3 hours, live acoustic guitarist or DJ, and Polaroid instant cameras with personalized guest favors.",
                "key_choices": [
                    "Dedicated bartender serving handcrafted artisanal drinks",
                    "Live musician for the first 90 minutes",
                    "Custom engraved acrylic cocktail stirrers & Polaroid guestbook"
                ]
            }
        },
        "timeline": [
            {"time": "T - 2:00", "action": "Atmosphere & Temperature Setup", "details": "Chill all white wines and garnishes, dim room lights, test audio volume from center of room."},
            {"time": "T - 0:15", "action": "Candles & Appetizer Display", "details": "Unveil charcuterie boards, light votive candles, start background playlist at 45% volume."},
            {"time": "T + 0:00", "action": "Arrivals & Signature Welcome Drink", "details": "Greet guests at door with a chilled signature cocktail in hand; immediate mood lift."},
            {"time": "T + 1:15", "action": "Warm Bites & Mingling", "details": "Brought out warm slider bites; raise music tempo to upbeat dance/funk."},
            {"time": "T + 2:30", "action": "Feature Toast & Photo Station Rush", "details": "Gather group for celebratory toast; encourage group snaps at the photo station."},
            {"time": "T + 4:00", "action": "Late-Night Sweet Treats & Wind Down", "details": "Serve espresso / dessert minis; lower music into mellow chillout tracks."}
        ],
        "music_and_vibe": {
            "vibe_description": f"Rich sensory ambiance keyed to '{theme}'. Low warm amber lighting accented with colored uplights matching theme colors.",
            "recommended_genres": ["Nu-Disco / Modern Funk", "Deep Tropical House", "Upbeat Indie Pop", "Smooth Lo-Fi Soul"],
            "lighting_setup": "Overhead lights off; 2700K warm string lights, 6-8 flickering LED tea lights, and a floor spotlight aimed at backdrop."
        },
        "cost_saving_hacks": [
            "Never offer an open individual-pour liquor bar: batch two striking signature cocktails in glass dispensers. You'll cut alcohol expenditure by up to 55%.",
            "Elevate finger food by using tiered slate boards and wooden risers from your kitchen; vertical display makes modest portions look decadent.",
            "Instead of hiring a photo booth company ($600+), buy an $18 ring light tripod with bluetooth remote and mount a decorative fabric backdrop."
        ],
        "total_allocated": budget
    }


# -------------------------------------------------------------
# 3. JEWELRY SELECTION & OUTFIT IMAGE ANALYSIS GENERATOR
# -------------------------------------------------------------
async def generate_jewelry_plan(
    occasion: str,
    neckline_outfit: str,
    metal_preference: str,
    budget: float,
    currency: str = "$",
    gemstone_preference: str = "Diamond / Moissanite / Clear Crystal",
    clothing_color: str = "Neutral / Navy",
    notes: str = "",
    image_bytes: Optional[bytes] = None,
    mime_type: str = "image/jpeg",
    user_api_key: Optional[str] = None
) -> Dict[str, Any]:
    
    prompt = f"""
    You are a celebrity fashion stylist and high-jewelry gemologist advisor.
    Provide a personalized jewelry curation and budget breakdown in strict JSON.
    Occasion: {occasion}
    Outfit Neckline / Silhouette: {neckline_outfit}
    Outfit Color / Description: {clothing_color}
    Preferred Metal: {metal_preference}
    Preferred Gemstones: {gemstone_preference}
    Total Budget: {currency}{budget:,.2f}
    Additional Notes: {notes or 'None'}
    {"An image of the outfit has been provided for multimodal visual analysis. Inspect its cut, neckline, color undertones, fabric texture, and formality." if image_bytes else ""}

    Return a JSON object with this exact structure:
    {{
      "title": "Evocative title for this jewelry curation",
      "outfit_analysis": {{
        "detected_style": "Deep description of the outfit silhouette, neckline, and aesthetic",
        "color_harmony": "Why the chosen metals and gems complement the clothing tones",
        "neckline_guidance": "Rule of balance for this neckline (e.g. why statement earrings + bare neck works, or why pendant length matters)"
      }},
      "curated_set": {{
        "primary_piece": {{
          "category": "Necklace / Statement Earrings",
          "name": "Piece Name",
          "est_cost": 300.00,
          "metal": "14k Gold Vermeil / Solid Gold / etc.",
          "gemstones": "Moissanite / Pearl / etc.",
          "styling_role": "Focal center of the ensemble"
        }},
        "earrings": {{
          "category": "Earrings",
          "name": "Piece Name",
          "est_cost": 150.00,
          "metal": "...",
          "gemstones": "...",
          "styling_role": "Framing the face"
        }},
        "wrist_piece": {{
          "category": "Bracelet / Cuff",
          "name": "Piece Name",
          "est_cost": 120.00,
          "metal": "...",
          "gemstones": "...",
          "styling_role": "Fluid movement"
        }},
        "finger_piece": {{
          "category": "Ring",
          "name": "Piece Name",
          "est_cost": 80.00,
          "metal": "...",
          "gemstones": "...",
          "styling_role": "Subtle tactile shine"
        }}
      }},
      "budget_breakdown": [
        {{
          "category": "Primary Statement / Complementary Accents / Metal Quality / Protective Storage",
          "percentage": 45,
          "allocated_amount": 250.00,
          "items": [
            {{"name": "Item Name", "est_cost": 180.00, "priority": "Investment Focal", "tip": "Carat / karat / sourcing recommendation"}}
          ]
        }}
      ],
      "tiers": {{
        "thrifty": {{"label": "Demi-Fine Fashion", "total": 0.70 * budget, "strategy": "Heavy 18k gold vermeil over sterling silver + cubic zirconia or lab pearls", "key_choices": ["...", "..."]}},
        "balanced": {{"label": "Fine Investment (Recommended)", "total": budget, "strategy": "10k/14k solid gold accents or certified moissanite", "key_choices": ["...", "..."]}},
        "luxe": {{"label": "Heirloom Luxury", "total": 1.40 * budget, "strategy": "18k solid gold & certified lab-grown diamonds", "key_choices": ["...", "..."]}}
      }},
      "styling_rules": [
        "Rule 1 on proportion",
        "Rule 2 on metal stacking",
        "Rule 3 on event endurance"
      ],
      "cost_saving_hacks": ["Smart jewelry hack 1", "Smart jewelry hack 2", "Smart jewelry hack 3"],
      "total_allocated": {budget}
    }}
    """

    gemini_result = await call_gemini_api(prompt, image_bytes=image_bytes, mime_type=mime_type, user_api_key=user_api_key)
    if gemini_result and "curated_set" in gemini_result:
        return gemini_result

    return get_fallback_jewelry_plan(occasion, neckline_outfit, metal_preference, budget, currency, gemstone_preference, clothing_color, notes, has_image=bool(image_bytes))


def get_fallback_jewelry_plan(
    occasion: str, neckline_outfit: str, metal_preference: str, budget: float, currency: str,
    gemstone_preference: str, clothing_color: str, notes: str, has_image: bool
) -> Dict[str, Any]:
    
    # Analyze neckline rules
    neckline_lower = neckline_outfit.lower()
    
    if "v-neck" in neckline_lower or "plunging" in neckline_lower:
        primary_cat = "Necklace"
        primary_name = f"Sculptural Lariat Y-Drop Pendant ({metal_preference})"
        primary_tip = "Matches the angle of the V-cut, drawing eyes harmoniously down without competing with fabric lines."
        earring_cat = "Huggie / Studs"
        earring_name = f"Bezel-Set Solitaire Studs or Dainty Huggies ({gemstone_preference})"
        earring_tip = "Keep earrings subtle to allow the V-lariat necklace to take center stage."
    elif "off-shoulder" in neckline_lower or "strapless" in neckline_lower:
        primary_cat = "Statement Earrings"
        primary_name = f"Cascading Chandelier or Tiered Drop Earrings ({gemstone_preference})"
        primary_tip = "Bare shoulders and collarbones provide an open stage for dramatic, movement-catching drop earrings."
        earring_cat = "Collarbone / Choker Accent"
        earring_name = f"Ultra-Dainty Floating Illusion Chain or Collar Choker"
        earring_tip = "Either keep the neck completely bare or wear a micro-chain that hugs the throat."
    elif "high-neck" in neckline_lower or "turtleneck" in neckline_lower or "halter" in neckline_lower:
        primary_cat = "Statement Cuff & Ring Stack"
        primary_name = f"Chunky Architectural Domed Bangle ({metal_preference})"
        primary_tip = "High fabric covers the chest, so shifting sparkle to forearms and hands creates balance."
        earring_cat = "Bold Ear Cuff / Statement Huggies"
        earring_name = f"Modern Bold Hoop or Textured C-Hoops ({metal_preference})"
        earring_tip = "Frame the jawline cleanly above the high fabric neckline."
    else: # Blazer, crewneck, casual
        primary_cat = "Layered Pendant Set"
        primary_name = f"Herringbone Flat Chain + Coin Medallion Duo ({metal_preference})"
        primary_tip = "Lends effortless structured luxury peeking beneath a blazer lapel or above a crew neckline."
        earring_cat = "Everyday Pavé Huggies"
        earring_name = f"Micro-Pavé Huggie Earrings ({gemstone_preference})"
        earring_tip = "Polished, versatile, and catches light with head movements."

    # Allocations
    primary_share = 0.44
    earrings_share = 0.26
    wrist_share = 0.18
    ring_share = 0.12

    p_alloc = round(budget * primary_share, 2)
    e_alloc = round(budget * earrings_share, 2)
    w_alloc = round(budget * wrist_share, 2)
    r_alloc = round(budget * ring_share, 2)

    curated_set = {
        "primary_piece": {
            "category": primary_cat,
            "name": primary_name,
            "est_cost": p_alloc,
            "metal": metal_preference,
            "gemstones": gemstone_preference,
            "styling_role": primary_tip
        },
        "earrings": {
            "category": "Earrings",
            "name": earring_name,
            "est_cost": e_alloc,
            "metal": metal_preference,
            "gemstones": gemstone_preference,
            "styling_role": earring_tip
        },
        "wrist_piece": {
            "category": "Bracelet / Bangle",
            "name": f"Classic Tennis Bracelet or Sleek Hinged Bangle ({metal_preference})",
            "est_cost": w_alloc,
            "metal": metal_preference,
            "gemstones": gemstone_preference,
            "styling_role": "Delicate sparkle that catches ambient candlelight during cocktails and conversation."
        },
        "finger_piece": {
            "category": "Ring",
            "name": f"Signet or Bezel-Set Solitaire Cocktail Ring ({metal_preference})",
            "est_cost": r_alloc,
            "metal": metal_preference,
            "gemstones": gemstone_preference,
            "styling_role": "Focal right-hand ring adding tailored personality."
        }
    }

    breakdown = [
        {
            "category": "Primary Anchor Piece",
            "percentage": 44,
            "allocated_amount": p_alloc,
            "items": [
                {"name": primary_name, "est_cost": p_alloc, "priority": "Focal Investment", "tip": f"Allocate the majority of your budget to this signature piece that anchors the gaze for {occasion}."}
            ]
        },
        {
            "category": "Facial Framing (Earrings)",
            "percentage": 26,
            "allocated_amount": e_alloc,
            "items": [
                {"name": earring_name, "est_cost": e_alloc, "priority": "High-Impact", "tip": "Choose secure lever-backs or screw-backs for worry-free wear during events."}
            ]
        },
        {
            "category": "Wrist & Hand Coordination",
            "percentage": 30,
            "allocated_amount": round(w_alloc + r_alloc, 2),
            "items": [
                {"name": curated_set["wrist_piece"]["name"], "est_cost": w_alloc, "priority": "Complementary", "tip": "Opt for 18k gold vermeil or surgical steel PVD plating for everyday scratch resistance."},
                {"name": curated_set["finger_piece"]["name"], "est_cost": r_alloc, "priority": "Finishing Accent", "tip": "Stack with existing heirloom bands or wear solo on the index finger."}
            ]
        }
    ]

    image_analysis_note = (
        f"Visual inspection of the uploaded outfit confirms an elegant drape in {clothing_color} tones with a prominent {neckline_outfit} silhouette. "
        if has_image else
        f"Based on your {clothing_color} ensemble and {neckline_outfit} cut, "
    )

    return {
        "title": f"The '{occasion}' Haute Curation in {metal_preference}",
        "outfit_analysis": {
            "detected_style": f"{image_analysis_note}Designed to elevate {occasion} styling without overpowering delicate garment stitching or neckline contours.",
            "color_harmony": f"The warm/cool sheen of {metal_preference} provides radiant contrast against {clothing_color}, while {gemstone_preference} adds refractive prism brilliance.",
            "neckline_guidance": f"For {neckline_outfit}: {primary_tip}"
        },
        "curated_set": curated_set,
        "budget_breakdown": breakdown,
        "tiers": {
            "thrifty": {
                "label": "Demi-Fine Gold Vermeil / Sterling",
                "total": round(budget * 0.70, 2),
                "strategy": "Heavy 2.5 micron 18k gold electroplating over 925 sterling silver with premium 5A cubic zirconia or freshwater baroque pearls.",
                "key_choices": [
                    "Gold vermeil lariat or hoop set with tarnish-resistant e-coating",
                    "Lab-created freshwater pearls with high organic luster",
                    "Micro-pavé detailing for indistinguishable diamond look"
                ]
            },
            "balanced": {
                "label": "Fine Investment (Recommended)",
                "total": round(budget, 2),
                "strategy": "14k solid gold primary piece with certified colorless Moissanite (higher fire dispersion than mined diamond) and solid silver accent stack.",
                "key_choices": [
                    "Solid gold focal chain that will never tarnish or lose color",
                    "GRA-certified D-color VVS1 Moissanite stones",
                    "Seamless clasp mechanisms built for lifetime wear"
                ]
            },
            "luxe": {
                "label": "High-Heirloom Luxury",
                "total": round(budget * 1.40, 2),
                "strategy": "Solid 18k yellow/white gold and IGI-certified lab-grown diamonds with exceptional clarity.",
                "key_choices": [
                    "Solid 18k gold cast pieces with heirloom weight and hallmarking",
                    "Certified lab diamonds (VS+ clarity, excellent cut)",
                    "Custom jeweler sizing and lifetime repolishing warranty"
                ]
            }
        },
        "styling_rules": [
            "Follow the 'One Diva' Rule: If your earrings are large and dramatic, keep the necklace understated or completely bare.",
            f"Harmonize with {metal_preference}: Coordinate belt buckles, handbag chains, and shoe accents to match the same metallic tone.",
            "Test Movement & Comfort: Ensure earrings weigh under 8 grams per ear to prevent stretching or discomfort across hours of celebration."
        ],
        "cost_saving_hacks": [
            "Opt for Moissanite or Lab-Grown gemstones over mined diamonds: identical hardness (9.25-10 Mohs scale), greater fiery sparkle, and 80-90% lower cost.",
            "Buy Demi-Fine (Gold Vermeil 2.5 micron on 925 silver) for trendy statement pieces and reserve Solid 14k/18k Gold exclusively for daily essentials (chains, studs).",
            "Clean jewelry at home with warm water, mild soap, and a soft baby toothbrush: restores maximum brilliance without paying for jeweler ultrasonic cleaning."
        ],
        "total_allocated": budget
    }
