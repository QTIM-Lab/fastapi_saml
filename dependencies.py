"""
Shared dependencies for route protection
"""
from fastapi import Request, HTTPException


async def require_auth(request: Request):
    """Simple auth check - require SAML authentication"""
    if not request.session.get('samlNameId'):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session