"""
Protected routes that require authentication
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dependencies import require_auth, require_auth_ui

from config import apps_and_users


router = APIRouter(tags=["protected"])
templates = Jinja2Templates(directory="templates")


@router.get("/protected")
async def protected_page(session = Depends(require_auth)):
    root_path = request.scope.get("root_path", "")
    # In production, you'd clear the user's session here
    return templates.TemplateResponse("protected.html", {"request": request, "root_path": root_path})


@router.get("/")
async def home(request: Request, session = Depends(require_auth_ui)):
    root_path = request.scope.get("root_path", "")
    samlNameId = request.session.get('samlNameId')

    # Example apps_and_users
    # apps_and_users = {
    #     "qtim_general_chatbot": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "QTIM General Chatbot", "location": "L40"},
    #     "qtim_grant_chatbot": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "QTIM Grant Chatbot", "location": "L40"},
    #     "ga_segmentation_app": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "GA Segmentation App", "location": "Linux Tower 2"},
    #     "cu_aai_dashboard": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "CU AAI Dashboard", "location": "Linux Tower 1"},
    #     "optimeyes": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "OPTIMEyes", "location": "Linux Tower 1"},
    #     "amd_classifier_app": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "AMD Classifier App", "location": "Linux Tower 2"},
    #     "l40": {"users": ['BENJAMIN.BEARCE@CUANSCHUTZ.EDU'], "display_name": "L40 Test", "location": "L40"},
    # }
    # pdb.set_trace()
    return templates.TemplateResponse("qtim_apps.html", {
        "request": request, 
        "root_path": root_path, 
        "samlNameId": samlNameId,
        "apps_and_users": apps_and_users})
