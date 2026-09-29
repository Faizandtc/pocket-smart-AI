from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    currency_pref: Optional[str] = "$"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    currency_pref: Optional[str] = "$"
    gemini_api_key: Optional[str] = None

class InteriorPlanRequest(BaseModel):
    title: Optional[str] = None
    room_type: str  # Living Room, Bedroom, Studio, Home Office, Kitchen, Dining Room, Balcony
    style: str      # Modern Minimalist, Scandinavian, Bohemian, Japandi, Industrial Luxe, Mid-Century
    dimensions: Optional[str] = "14x12 ft"
    budget: float = Field(..., gt=0)
    currency: Optional[str] = "$"
    special_requirements: Optional[str] = ""
    target_palette: Optional[str] = "Warm Neutrals & Accents"

class PartyPlanRequest(BaseModel):
    title: Optional[str] = None
    event_type: str # Birthday, Wedding Reception, Cocktail Mixer, Dinner Party, Tech Meetup, Baby Shower
    guest_count: int = Field(..., gt=0)
    theme: str      # Neon Cyberpunk, Rustic Garden, Gatsby Glamour, Tropical Sunset, Casual Chic
    budget: float = Field(..., gt=0)
    currency: Optional[str] = "$"
    venue_type: Optional[str] = "Indoor Apartment / Home"
    special_notes: Optional[str] = ""

class JewelryPlanRequest(BaseModel):
    title: Optional[str] = None
    occasion: str   # Wedding Guest, Gala / Black Tie, Daily Minimalist, Cocktail Date, Festive
    neckline_outfit: str # V-Neck, Off-Shoulder, Sweetheart, Halter, High-Neck, Crewneck, Blazer
    metal_preference: str # Yellow Gold, White Gold / Silver, Rose Gold, Mixed Metals
    gemstone_preference: Optional[str] = "Diamond / Moissanite / Clear Crystal"
    budget: float = Field(..., gt=0)
    currency: Optional[str] = "$"
    clothing_color: Optional[str] = "Neutral / Navy"
    notes: Optional[str] = ""

class FavoriteToggleRequest(BaseModel):
    is_favorite: bool
