"""
Helper functions for SAML authentication
"""
from fastapi import Request
from onelogin.saml2.auth import OneLogin_Saml2_Auth

from config import SAML_SETTINGS

def init_saml_auth(req):
    """Initialize SAML auth object"""
    auth = OneLogin_Saml2_Auth(req, SAML_SETTINGS)
    return auth


def prepare_fastapi_request(request: Request):
    """Convert FastAPI request to format expected by python3-saml"""
    url_data = {
        "https": "on" if request.url.scheme == "https" else "off",
        "http_host": request.client.host if request.client else "localhost",
        "server_port": request.url.port,
        "script_name": request.url.path,
        "get_data": dict(request.query_params),
        "post_data": {}
    }
    return {
        "https": url_data["https"],
        "http_host": request.headers.get("host", url_data["http_host"]),
        "script_name": url_data["script_name"],
        "server_port": url_data["server_port"],
        "get_data": url_data["get_data"],
        "post_data": url_data["post_data"]
    }