import json
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from app.database import get_db_connection
from app.auth import get_optional_current_user, get_current_user
from app.models import PartyPlanRequest
from app.gemini_service import generate_party_plan
from app.templating import render_template

router = APIRouter()

@router.get("/party", response_class=HTMLResponse)
async def party_page(request: Request, user=Depends(get_optional_current_user)):
    return render_template(request, "party.html", {
        "user": user,
        "currency": user.get("currency_pref", "$") if user else "$"
    })

@router.post("/api/party/generate")
async def generate_party_api(
    req: PartyPlanRequest,
    user=Depends(get_current_user)
):
    try:
        currency = req.currency or user.get("currency_pref", "$")
        user_key = user.get("gemini_api_key")

        plan_result = await generate_party_plan(
            event_type=req.event_type,
            guest_count=req.guest_count,
            theme=req.theme,
            budget=req.budget,
            currency=currency,
            venue_type=req.venue_type or "Indoor Apartment / Home",
            special_notes=req.special_notes or "",
            user_api_key=user_key
        )

        title = req.title or plan_result.get("title", f"{req.theme} {req.event_type}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations (user_id, category, title, budget, currency, input_params, result_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"],
            "party",
            title,
            req.budget,
            currency,
            json.dumps(req.model_dump()),
            json.dumps(plan_result)
        ))
        conn.commit()
        plan_id = cursor.lastrowid
        conn.close()

        return JSONResponse(content={
            "success": True,
            "plan_id": plan_id,
            "plan": plan_result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
