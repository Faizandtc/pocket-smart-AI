import json
import uuid
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from app.config import UPLOAD_DIR
from app.database import get_db_connection
from app.auth import get_optional_current_user, get_current_user
from app.gemini_service import generate_jewelry_plan
from app.templating import render_template

router = APIRouter()

@router.get("/jewelry", response_class=HTMLResponse)
async def jewelry_page(request: Request, user=Depends(get_optional_current_user)):
    return render_template(request, "jewelry.html", {
        "user": user,
        "currency": user.get("currency_pref", "$") if user else "$"
    })

@router.post("/api/jewelry/generate")
async def generate_jewelry_api(
    occasion: str = Form(...),
    neckline_outfit: str = Form(...),
    metal_preference: str = Form(...),
    budget: float = Form(...),
    gemstone_preference: str = Form("Diamond / Moissanite / Clear Crystal"),
    clothing_color: str = Form("Neutral / Navy"),
    notes: str = Form(""),
    title: Optional[str] = Form(None),
    currency: Optional[str] = Form(None),
    outfit_image: Optional[UploadFile] = File(None),
    user=Depends(get_current_user)
):
    try:
        user_currency = currency or user.get("currency_pref", "$")
        user_key = user.get("gemini_api_key")

        image_path_saved = None
        image_bytes = None
        mime_type = "image/jpeg"

        if outfit_image and outfit_image.filename:
            ext = Path(outfit_image.filename).suffix.lower()
            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                image_bytes = await outfit_image.read()
                filename = f"outfit_{uuid.uuid4().hex[:12]}{ext}"
                save_destination = UPLOAD_DIR / filename
                with open(save_destination, "wb") as f:
                    f.write(image_bytes)
                image_path_saved = f"/uploads/{filename}"
                mime_type = outfit_image.content_type or ("image/png" if ext == ".png" else "image/jpeg")

        plan_result = await generate_jewelry_plan(
            occasion=occasion,
            neckline_outfit=neckline_outfit,
            metal_preference=metal_preference,
            budget=budget,
            currency=user_currency,
            gemstone_preference=gemstone_preference,
            clothing_color=clothing_color,
            notes=notes,
            image_bytes=image_bytes,
            mime_type=mime_type,
            user_api_key=user_key
        )

        plan_title = title or plan_result.get("title", f"{occasion} Jewelry Curation")

        input_data = {
            "occasion": occasion,
            "neckline_outfit": neckline_outfit,
            "metal_preference": metal_preference,
            "gemstone_preference": gemstone_preference,
            "budget": budget,
            "currency": user_currency,
            "clothing_color": clothing_color,
            "notes": notes,
            "has_image": bool(image_path_saved)
        }

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations (user_id, category, title, budget, currency, input_params, result_data, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"],
            "jewelry",
            plan_title,
            budget,
            user_currency,
            json.dumps(input_data),
            json.dumps(plan_result),
            image_path_saved
        ))
        conn.commit()
        plan_id = cursor.lastrowid
        conn.close()

        return JSONResponse(content={
            "success": True,
            "plan_id": plan_id,
            "plan": plan_result,
            "image_url": image_path_saved
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
