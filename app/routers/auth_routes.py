from fastapi import APIRouter, Request, Response, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.database import get_db_connection
from app.auth import hash_password, verify_password, create_access_token, get_optional_current_user
from app.templating import render_template

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return render_template(request, "login.html", {"user": None, "error": None})

@router.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password_hash, full_name, currency_pref FROM users WHERE email = ?", (email.strip().lower(),))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row or not verify_password(password, user_row["password_hash"]):
        return render_template(request, "login.html", {
            "user": None,
            "error": "Invalid email or password. Please try again.",
            "email": email
        }, status_code=status.HTTP_401_UNAUTHORIZED)

    # Valid user: generate JWT
    token = create_access_token(data={"sub": str(user_row["id"]), "username": user_row["username"]})
    
    redirect_resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    redirect_resp.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=86400,
        samesite="lax",
        secure=False
    )
    return redirect_resp

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user=Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return render_template(request, "register.html", {"user": None, "error": None})

@router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(""),
    currency_pref: str = Form("$")
):
    cleaned_email = email.strip().lower()
    cleaned_username = username.strip()

    if len(password) < 6:
        return render_template(request, "register.html", {
            "user": None,
            "error": "Password must be at least 6 characters long.",
            "username": cleaned_username,
            "email": cleaned_email,
            "full_name": full_name
        }, status_code=400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (cleaned_email, cleaned_username))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return render_template(request, "register.html", {
            "user": None,
            "error": "An account with that email or username already exists.",
            "username": cleaned_username,
            "email": cleaned_email,
            "full_name": full_name
        }, status_code=400)

    hashed = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name, currency_pref) VALUES (?, ?, ?, ?, ?)",
        (cleaned_username, cleaned_email, hashed, full_name.strip() or cleaned_username, currency_pref)
    )
    conn.commit()
    new_user_id = cursor.lastrowid
    conn.close()

    token = create_access_token(data={"sub": str(new_user_id), "username": cleaned_username})
    redirect_resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    redirect_resp.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=86400,
        samesite="lax",
        secure=False
    )
    return redirect_resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie(key="access_token")
    return resp
