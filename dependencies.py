"""
Shared dependencies for route protection
"""
import pdb
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse


async def require_auth(request: Request):
    """Simple auth check - require SAML authentication"""
    if not request.session.get('samlNameId'):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session


async def require_auth_ui(request: Request):
    if request.session.get("samlNameId") is None:
        redirect_url = f"/saml/login?redirect={request.url.path}"
        raise HTTPException(
            status_code=303,
            headers={"Location": redirect_url},
        )
    return request.session