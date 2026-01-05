"""
Protected routes that require authentication
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dependencies import require_auth

router = APIRouter(tags=["protected"])
templates = Jinja2Templates(directory="templates")


@router.get("/protected")
async def protected_page(session = Depends(require_auth)):
    root_path = request.scope.get("root_path", "")
    # In production, you'd clear the user's session here
    return templates.TemplateResponse("protected.html", {"request": request, "root_path": root_path})

    return HTMLResponse(f"<h1>Hello {session['samlNameId']}!</h1>")
