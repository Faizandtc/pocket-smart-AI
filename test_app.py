import asyncio
import io
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.auth import initialize_auth

def run_tests():
    print("Testing PocketSmart AI Application...")
    init_db()
    initialize_auth()

    client = TestClient(app)

    # 1. Test Landing Page
    resp = client.get("/")
    assert resp.status_code == 200
    assert "PocketSmart" in resp.text
    print(" [x] GET / Landing page OK")

    # 2. Test Login with Demo User
    resp = client.post("/login", data={"email": "demo@pocketsmart.ai", "password": "password123"}, follow_redirects=False)
    assert resp.status_code == 302
    assert "access_token" in resp.cookies
    token_cookie = resp.cookies["access_token"]
    print(" [x] POST /login Demo user auth OK")

    # 3. Test Dashboard with Cookie
    resp = client.get("/dashboard", cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    assert "Alex Morgan" in resp.text or "demo_user" in resp.text
    print(" [x] GET /dashboard Protected route OK")

    # 4. Test Home Interior Generation
    interior_payload = {
        "room_type": "Living Room",
        "style": "Modern Minimalist",
        "dimensions": "16x14 ft",
        "budget": 3500.0,
        "currency": "$",
        "special_requirements": "Spacious seating, pet-friendly rug"
    }
    resp = client.post("/api/interior/generate", json=interior_payload, cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    int_data = resp.json()
    assert int_data["success"] is True
    assert "plan" in int_data
    assert "color_palette" in int_data["plan"]
    assert "budget_breakdown" in int_data["plan"]
    assert "tiers" in int_data["plan"]
    interior_plan_id = int_data["plan_id"]
    print(f" [x] POST /api/interior/generate OK (Plan ID: {interior_plan_id})")

    # 5. Test Party Generation
    party_payload = {
        "event_type": "Cocktail Mixer / Soirée",
        "theme": "Neon Cyberpunk",
        "guest_count": 30,
        "budget": 2400.0,
        "currency": "$",
        "venue_type": "Rented Loft",
        "special_notes": "Signature gin drinks, high energy"
    }
    resp = client.post("/api/party/generate", json=party_payload, cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    pty_data = resp.json()
    assert pty_data["success"] is True
    assert "timeline" in pty_data["plan"]
    party_plan_id = pty_data["plan_id"]
    print(f" [x] POST /api/party/generate OK (Plan ID: {party_plan_id})")

    # 6. Test Jewelry Generation with optional outfit image
    fake_image_file = ("dress.jpg", io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"), "image/jpeg")
    
    jewelry_data = {
        "occasion": "Gala / Black Tie",
        "neckline_outfit": "Plunging V-Neck",
        "metal_preference": "Yellow Gold",
        "gemstone_preference": "Diamond / Moissanite",
        "clothing_color": "Midnight Navy Silk",
        "budget": "1800",
        "currency": "$"
    }
    resp = client.post(
        "/api/jewelry/generate",
        data=jewelry_data,
        files={"outfit_image": fake_image_file},
        cookies={"access_token": token_cookie}
    )
    assert resp.status_code == 200
    jwl_data = resp.json()
    assert jwl_data["success"] is True
    assert "curated_set" in jwl_data["plan"]
    assert "outfit_analysis" in jwl_data["plan"]
    jewelry_plan_id = jwl_data["plan_id"]
    print(f" [x] POST /api/jewelry/generate with Outfit Image OK (Plan ID: {jewelry_plan_id})")

    # 7. Test History Page
    resp = client.get("/history", cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    assert "Recommendation History" in resp.text
    print(" [x] GET /history Library view OK")

    # 8. Test Plan Detail Page
    resp = client.get(f"/plan/{interior_plan_id}", cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    assert "Color Palette" in resp.text
    print(f" [x] GET /plan/{interior_plan_id} Detail view OK")

    # 9. Test Favorite Toggle API
    resp = client.post(f"/api/plans/{interior_plan_id}/favorite", json={"is_favorite": True}, cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True
    print(" [x] POST /api/plans/{id}/favorite OK")

    # 10. Test Settings update
    resp = client.post("/settings", data={"full_name": "Alex Morgan Updated", "currency_pref": "$", "gemini_api_key": ""}, cookies={"access_token": token_cookie})
    assert resp.status_code == 200
    assert "Alex Morgan Updated" in resp.text
    print(" [x] POST /settings Update preferences OK")

    print("\n==============================================")
    print("SUCCESS: ALL 10 TEST SUITES PASSED FLAWLESSLY!")
    print("==============================================\n")

if __name__ == "__main__":
    run_tests()
