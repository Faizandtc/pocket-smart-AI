import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db_connection
from app.auth import get_current_user
from app.models import FavoriteToggleRequest

router = APIRouter(prefix="/api")

@router.get("/plans")
async def get_plans(category: str = None, user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("""
            SELECT id, category, title, budget, currency, result_data, image_path, is_favorite, created_at
            FROM recommendations
            WHERE user_id = ? AND category = ?
            ORDER BY created_at DESC
        """, (user["id"], category))
    else:
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
            "currency": r["currency"],
            "image_path": r["image_path"],
            "is_favorite": bool(r["is_favorite"]),
            "created_at": r["created_at"],
            "summary": data.get("summary", "")
        })

    return JSONResponse(content={"plans": plans})

@router.get("/plans/{plan_id}")
async def get_plan_detail(plan_id: int, user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, title, budget, currency, input_params, result_data, image_path, is_favorite, created_at
        FROM recommendations
        WHERE id = ? AND user_id = ?
    """, (plan_id, user["id"]))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    return JSONResponse(content={
        "id": row["id"],
        "category": row["category"],
        "title": row["title"],
        "budget": row["budget"],
        "currency": row["currency"],
        "input_params": json.loads(row["input_params"]),
        "result_data": json.loads(row["result_data"]),
        "image_path": row["image_path"],
        "is_favorite": bool(row["is_favorite"]),
        "created_at": row["created_at"]
    })

@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: int, user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendations WHERE id = ? AND user_id = ?", (plan_id, user["id"]))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Plan not found or not authorized")

    return JSONResponse(content={"success": True, "message": "Plan deleted successfully"})

@router.post("/plans/{plan_id}/favorite")
async def toggle_favorite(plan_id: int, req: FavoriteToggleRequest, user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recommendations
        SET is_favorite = ?
        WHERE id = ? AND user_id = ?
    """, (1 if req.is_favorite else 0, plan_id, user["id"]))
    conn.commit()
    conn.close()

    return JSONResponse(content={"success": True, "is_favorite": req.is_favorite})
