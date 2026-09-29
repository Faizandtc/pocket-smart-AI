import json
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from app.database import get_db_connection
from app.auth import get_optional_current_user, get_current_user
from app.models import InteriorPlanRequest
from app.gemini_service import generate_interior_plan
from app.templating import render_template

router = APIRouter()

@router.get("/interior", response_class=HTMLResponse)
async def interior_page(request: Request, user=Depends(get_optional_current_user)):
    return render_template(request, "interior.html", {
        "user": user,
        "currency": user.get("currency_pref", "$") if user else "$"
    })

@router.post("/api/interior/generate")
async def generate_interior_api(
    req: InteriorPlanRequest,
    user=Depends(get_current_user)
):
    try:
        currency = req.currency or user.get("currency_pref", "$")
        user_key = user.get("gemini_api_key")

        plan_result = await generate_interior_plan(
            room_type=req.room_type,
            style=req.style,
            dimensions=req.dimensions or "14x12 ft",
            budget=req.budget,
            currency=currency,
            special_requirements=req.special_requirements or "",
            target_palette=req.target_palette or "Warm Neutrals & Accents",
            user_api_key=user_key
        )

        title = req.title or plan_result.get("title", f"{req.style} {req.room_type} Plan")

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations (user_id, category, title, budget, currency, input_params, result_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"],
            "interior",
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
