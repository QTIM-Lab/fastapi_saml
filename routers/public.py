"""
Protected routes that require authentication
"""
import pdb
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dependencies import require_auth

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="templates")

@router.get("/public")
async def test_public():
    """Public endpoint - no authentication required"""
    return {"message": "This is a public endpoint", "authentication": "not required"}


@router.get("/index")
async def home(request: Request):
    root_path = request.scope.get("root_path", "")
    return templates.TemplateResponse("index.html", {"request": request, "root_path": root_path})


@router.get("/")
async def home(request: Request):
    root_path = request.scope.get("root_path", "")
    return templates.TemplateResponse("qtim_apps.html", {"request": request, "root_path": root_path})
