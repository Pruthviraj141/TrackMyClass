"""
Auth Router.
Handles login and logout endpoints for Admin and Student.
"""
import uuid

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.auth import (
    verify_admin_credentials,
    verify_student_credentials,
    create_auth_session,
    destroy_auth_session,
)
from backend.config import TEMPLATES_DIR

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Unified login page with Admin / Student tabs."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    login_type: str = Form("admin"),
    username: str = Form(""),
    password: str = Form(...),
    roll_number: str = Form(""),
):
    """Handle both admin and student login from the same form."""
    if login_type == "admin":
        # Admin login
        if verify_admin_credentials(username, password):
            session_id = str(uuid.uuid4())
            create_auth_session(session_id, role="admin", user_id="admin", name="Admin")
            response = RedirectResponse(url="/admin/dashboard", status_code=303)
            response.set_cookie(key="session_id", value=session_id, httponly=True)
            return response

        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid admin credentials.", "tab": "admin"},
        )

    elif login_type == "student":
        # Student login
        student = verify_student_credentials(roll_number, password)
        if student:
            session_id = str(uuid.uuid4())
            create_auth_session(
                session_id,
                role="student",
                user_id=student["student_id"],
                name=student["name"],
            )
            response = RedirectResponse(url="/student/dashboard", status_code=303)
            response.set_cookie(key="session_id", value=session_id, httponly=True)
            return response

        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid roll number or password.", "tab": "student"},
        )

    # Fallback
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid login type."},
    )


@router.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        destroy_auth_session(session_id)

    response = RedirectResponse(url="/login")
    response.delete_cookie("session_id")
    return response
