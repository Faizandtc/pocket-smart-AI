import json
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import get_db_connection
from app.auth import get_current_user, get_optional_current_user
from app.templating import render_template

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, user=Depends(get_optional_current_user)):
    return render_template(request, "index.html", {"user": user})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user=Depends(get_optional_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch user plans
    cursor.execute("""
        SELECT id, category, title, budget, currency, result_data, image_path, is_favorite, created_at
        FROM recommendations
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user["id"],))
    rows = cursor.fetchall()
    conn.close()

    plans = []
    total_budget_planned = 0.0
    category_counts = {"interior": 0, "party": 0, "jewelry": 0}

    for r in rows:
        try:
            parsed_data = json.loads(r["result_data"])
        except Exception:
            parsed_data = {}
            
        plans.append({
            "id": r["id"],
            "category": r["category"],
            "title": r["title"],
            "budget": r["budget"],
            "currency": r["currency"] or user.get("currency_pref", "$"),
            "image_path": r["image_path"],
            "is_favorite": bool(r["is_favorite"]),
            "created_at": r["created_at"],
            "data": parsed_data
        })
        total_budget_planned += float(r["budget"])
        cat = r["category"].lower()
        if cat in category_counts:
            category_counts[cat] += 1

    # Determine favorite category
    favorite_cat = max(category_counts, key=category_counts.get) if total_budget_planned > 0 else "None yet"
    cat_display = {
        "interior": "Home Interior",
        "party": "Party & Events",
        "jewelry": "Jewelry & Outfit",
        "None yet": "Explore Planners"
    }

    stats = {
        "total_plans": len(plans),
        "total_budget": round(total_budget_planned, 2),
        "favorite_category": cat_display.get(favorite_cat, favorite_cat.title()),
        "category_counts": category_counts
    }

    return render_template(request, "dashboard.html", {
        "user": user,
        "stats": stats,
        "recent_plans": plans[:6],
        "all_plans_json": json.dumps(category_counts)
    })

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, user=Depends(get_optional_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, title, budget, currency, result_data, image_path, is_favorite, created_at
        FROM recommendations
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user["id"],))
    rows = cursor.fetchall()
    conn.close()

    plans = []
    for r in rows:
        try:
            data = json.loads(r["result_data"])
        except Exception:
            data = {}
        plans.append({
            "id": r["id"],
            "category": r["category"],
            "title": r["title"],
            "budget": r["budget"],
            "currency": r["currency"] or "$",
            "image_path": r["image_path"],
            "is_favorite": bool(r["is_favorite"]),
            "created_at": r["created_at"],
            "summary": data.get("summary", "")
        })

    return render_template(request, "history.html", {
        "user": user,
        "plans": plans
    })

@router.get("/plan/{plan_id}", response_class=HTMLResponse)
async def plan_detail_page(plan_id: int, request: Request, user=Depends(get_optional_current_user)):
    if not user:
        return RedirectResponse(url=f"/login?next=/plan/{plan_id}", status_code=status.HTTP_302_FOUND)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, category, title, budget, currency, input_params, result_data, image_path, is_favorite, created_at
        FROM recommendations
        WHERE id = ? AND user_id = ?
    """, (plan_id, user["id"]))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Recommendation plan not found")

    try:
        input_params = json.loads(row["input_params"])
        result_data = json.loads(row["result_data"])
    except Exception:
        input_params = {}
        result_data = {}

    plan = {
        "id": row["id"],
        "category": row["category"],
        "title": row["title"],
        "budget": row["budget"],
        "currency": row["currency"] or "$",
        "input_params": input_params,
        "result_data": result_data,
        "image_path": row["image_path"],
        "is_favorite": bool(row["is_favorite"]),
        "created_at": row["created_at"]
    }

    return render_template(request, "plan_detail.html", {
        "user": user,
        "plan": plan,
        "raw_json": json.dumps(result_data)
    })

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user=Depends(get_optional_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return render_template(request, "settings.html", {"user": user, "message": None})

@router.post("/settings")
async def update_settings(
    request: Request,
    full_name: str = Form(""),
    currency_pref: str = Form("$"),
    gemini_api_key: str = Form(""),
    user=Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET full_name = ?, currency_pref = ?, gemini_api_key = ?
        WHERE id = ?
    """, (full_name.strip(), currency_pref.strip(), gemini_api_key.strip() or None, user["id"]))
    conn.commit()
    
    # Reload updated user
    cursor.execute("SELECT id, username, email, full_name, gemini_api_key, currency_pref, created_at FROM users WHERE id = ?", (user["id"],))
    updated_user = dict(cursor.fetchone())
    conn.close()

    return render_template(request, "settings.html", {
        "user": updated_user,
        "message": "Settings updated successfully! Your preferences are active."
    })
