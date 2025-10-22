"""
Protected routes that require authentication
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from dependencies import require_auth

router = APIRouter(tags=["protected"])


@router.get("/protected")
async def protected_page(session = Depends(require_auth)):
    return HTMLResponse(f"<h1>Hello {session['samlNameId']}!</h1>")

