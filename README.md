# 💎 PocketSmart AI

> **Budget-First AI Lifestyle & Event Recommendation System**  
> Built with **FastAPI, Gemini AI, SQLite, JWT Authentication, HTML/CSS/JavaScript, and Jinja2**.

---

## 🌟 Overview

**PocketSmart AI** is a financial lifestyle planning application that eliminates guesswork when spending money on major life moments. Powered by **Google Gemini AI** (with an intelligent domain-expert fallback engine), it formulates structured, transparent budget breakdowns across three primary pillars:

1. 🛋️ **Home Interior Planning**
   - Room-type dimensional analysis (Living Room, Master Bedroom, Studio, Home Office...)
   - Cohesive 4-shade harmonic color palettes with hex values and design rationales
   - Precision budget allocation across Core Furniture, Lighting, Soft Goods & Rugs, Art, and Hardware Contingency
   - Spatial placement advice and clever budget-saving DIY hacks
   - **3-Tier Analysis**: Thrifty Saver (~78%), Balanced Designer (100%), and Luxe Bespoke (~130%)

2. 🎉 **Party & Event Planning**
   - Event types (Birthdays, Cocktail Mixers, Receptions, Game Nights, Tech Meetups...)
   - Dynamic per-guest metric calculator (`$Budget / Guests`)
   - Complete itemized catering, signature craft cocktail batching, ambient lighting, and audio curation
   - **Minute-by-Minute Run of Show Host Choreography Timeline**
   - High-impact DIY hacks (Canva printable signage, photo booth phone mounts, signature batching)

3. 💎 **Jewelry Selection & Outfit-Image Analysis**
   - **Multimodal AI Vision**: Upload dress / outfit photos (PNG, JPG, WebP) with instant client-side thumbnail preview
   - Inspects necklines (V-Neck, Off-Shoulder, Turtleneck, Strapless, Blazer...) and color tones
   - Curates a complete **4-Piece Coordinated Suite** (Focal Statement, Facial Framing Earrings, Wrist Movement, Accent Ring)
   - Metal harmony guidance (Yellow Gold, White Gold, Rose Gold, Mixed Metals)
   - Quality pricing tiers: Demi-Fine Vermeil, Fine Moissanite, and Heirloom Solid Gold

---

## 🚀 Key Features

- **🔐 Dual JWT Authentication**:
  - Secure bcrypt password hashing.
  - HTTP-only cookie support for smooth Jinja2 multi-page transitions.
  - Optional `Authorization: Bearer <token>` support for REST clients.
  - Pre-seeded instant demo reviewer account.
- **📊 Interactive Visuals**:
  - Live Chart.js doughnut charts visualizing category shares.
  - Interactive budget simulator directly on the landing page.
  - Dynamic 3-tier tab switchers updating items and strategies instantly.
- **📜 Recommendation History & Management**:
  - SQLite database persistence with relational foreign keys.
  - Category filtering (Interior, Party, Jewelry), live title search, and favorite toggles.
  - Dedicated printable plan details view (`/plan/{id}`) with print/PDF styling and clipboard copy.
- **⚙️ User Settings & API Configuration**:
  - Manage user profile, customize currency symbols (`$`, `€`, `£`, `₹`, `¥`, `C$`), and optionally provide a personal Gemini API key.
- **📱 Responsive & Modern UI**:
  - Tailwind CSS 3.4 with custom glassmorphism effects, Lucide icons, responsive navigation, and mobile hamburger drawer.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13+, FastAPI, Uvicorn, Jinja2, python-multipart, PyJWT, bcrypt, httpx, python-dotenv
- **Database**: SQLite3 (zero-configuration local persistence)
- **AI Engine**: Google Generative AI (Gemini 2.5 Flash / 1.5 Flash multimodal REST API) + Built-in domain-expert fallback
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), Tailwind CSS (CDN), Chart.js (CDN), Lucide Icons

---

## 🏃 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Installation
Clone or navigate to the project directory:
```bash
cd pocketsmart-ai
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your `GEMINI_API_KEY` to `.env`, or configure it directly inside the app's **Settings** page. If left blank, PocketSmart AI will automatically run its rich built-in simulation generator.

### 4. Run the Application
```bash
python run.py
```
Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser at:
👉 **`http://127.0.0.1:8000`**

---

## 🔑 Pre-Seeded Demo Account
For rapid evaluation, the app automatically initializes a demo user:
- **Email**: `demo@pocketsmart.ai`
- **Password**: `password123`
*(A "Fill Demo" shortcut button is also available on the `/login` screen)*

---

## 📂 Project Structure

```
pocketsmart-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization, routes, lifespan
│   ├── config.py                 # Configuration, paths, environment variables
│   ├── database.py               # SQLite schema setup and DB connection helpers
│   ├── models.py                 # Pydantic request models
│   ├── auth.py                   # Bcrypt hashing, JWT generation/decoding, user dependency
│   ├── gemini_service.py         # Gemini multimodal API client + fallback expert engine
│   ├── routers/
│   │   ├── auth_routes.py        # Login, registration, and logout
│   │   ├── dashboard_routes.py   # Landing, dashboard, history, plan detail, settings
│   │   ├── interior_routes.py    # Home interior planner views and generation API
│   │   ├── party_routes.py       # Party & event planner views and generation API
│   │   ├── jewelry_routes.py     # Jewelry & outfit vision planner with image upload
│   │   └── api_routes.py         # AJAX endpoints (plans list, favorites, delete)
│   ├── static/
│   │   ├── css/custom.css        # Glassmorphism, animations, print layout
│   │   ├── js/
│   │   │   ├── app.js            # Global helper functions, currency, Chart.js utils
│   │   │   ├── interior.js       # Interior planner AJAX & DOM logic
│   │   │   ├── party.js          # Party planner timeline & per-guest calculation
│   │   │   └── jewelry.js        # Multimodal image dropzone & 4-piece suite renderer
│   │   └── images/logo.svg       # Brand vector SVG logo
│   └── templates/
│       ├── base.html             # Base Jinja2 layout with navbar & toast alerts
│       ├── index.html            # Landing page with live budget preview simulator
│       ├── login.html            # Sign-in with quick demo button
│       ├── register.html         # User sign-up with currency selector
│       ├── dashboard.html        # Metrics cards, category donut chart, recent plans
│       ├── interior.html         # Interior room planner view
│       ├── party.html            # Party planning view
│       ├── jewelry.html          # Jewelry & outfit image upload view
│       ├── history.html          # Full recommendations library with search & filter
│       ├── plan_detail.html      # Printable detailed report view
│       └── settings.html         # Profile, currency, and Gemini API key settings
├── uploads/                      # Uploaded outfit images
├── .env.example
├── .env
├── requirements.txt
├── README.md
└── run.py                        # Easy server launcher
```

---

## 🔒 Security
- Passwords are encrypted using salted `bcrypt` hashes.
- Session tokens are signed with HMAC-SHA256 (`HS256`) and delivered via secure `access_token` cookies.
- All database operations utilize parameterized queries (`?`) to prevent SQL injection.
- User files are validated for permitted image extensions and assigned random hex UUIDs.
