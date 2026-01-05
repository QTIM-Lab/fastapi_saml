"""
SAML authentication routes
"""
import pdb
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from utils.saml_helpers import init_saml_auth, prepare_fastapi_request
from config import DEBUG

router = APIRouter(prefix="/saml", tags=["saml"])
templates = Jinja2Templates(directory="templates")


@router.get("/validate")
async def validate(request: Request):
    """
    Endpoint for nginx auth_request
    Returns 200 if user is authenticated, 401 if not
    """
    # Check if session contains SAML authentication data
    saml_name_id = request.session.get('samlNameId')
    saml_userdata = request.session.get('samlUserdata')
    # request.session.clear()
    if saml_name_id:
        if saml_userdata:
            # User is authenticated - return user info in headers
            email = saml_userdata.get('email', [''])[0] if saml_userdata.get('email') else ''
            name = saml_userdata.get('name', [''])[0] if saml_userdata.get('name') else ''
        return Response(
            status_code=200,
            headers={
                "X-User-Email": email if email else "",
                "X-User-Name": name if name else "",
                "X-User-NameId": saml_name_id
            }
        )
    return Response(status_code=401)


@router.get("/login")
async def saml_login(request: Request):
    """Initiate SAML SSO login - redirects to Okta"""
    redirect_url = request.query_params.get("redirect", "/")

    req = prepare_fastapi_request(request)
    auth = init_saml_auth(req)
    
    # Redirect to Okta for authentication
    sso_url = auth.login(return_to=redirect_url)
    return RedirectResponse(url=sso_url)


# Same as logout basically...merge
@router.get("/clear_session")
async def validate(request: Request):
    """
    Test endpoint to clear session
    """
    request.session.clear()
    return Response(
        status_code=200,
        headers={
            "X-User-Email": "unset",
            "X-User-Name": "unset",
            "X-User-NameId": "unset"
        }
    )


@router.get("/logout")
async def saml_logout(request: Request):
    """Simple logout - clears local session and provides Okta logout link"""
    request.session.clear()
    root_path = request.scope.get("root_path", "")
    # In production, you'd clear the user's session here
    return templates.TemplateResponse("logout.html", {"request": request, "root_path": root_path})


@router.post("/acs")
async def saml_acs(request: Request):
    """
    Assertion Consumer Service - Okta posts SAML response here after authentication
    This is the callback URL you configure in Okta
    """
    req = prepare_fastapi_request(request)
    
    # Get POST data
    form_data = await request.form()
    req["post_data"] = dict(form_data)
    
    # Get RelayState from the SAML response
    relay_state = form_data.get("RelayState", "/protected")

    auth = init_saml_auth(req)
    auth.process_response()
    
    errors = auth.get_errors()
    
    if len(errors) == 0:
        if not auth.is_authenticated():
            return HTMLResponse(
                content="<h1>Not authenticated</h1><p>User is not authenticated.</p>",
                status_code=401
            )
        
        # Successfully authenticated - get user attributes
        user_data = {
            "nameid": auth.get_nameid(),
            "attributes": auth.get_attributes(),
            "session_index": auth.get_session_index()
        }

        # set session data
        request.session['samlNameId'] = auth.get_nameid()
        request.session['samlUserdata'] = auth.get_attributes()
        
        # In production, you'd create a session here
        # For demo, just show the user data
        if DEBUG == 'True':
            root_path = request.scope.get("root_path", "")
            # In production, you'd clear the user's session here
            return templates.TemplateResponse("acs.html", {"request": request, "root_path": root_path, "user_data": user_data})
        else:

            return RedirectResponse(url=relay_state, status_code=303)     
    else:
        error_msg = ", ".join(errors)
        error_reason = auth.get_last_error_reason()
        return HTMLResponse(
            content=f"<h1>Error</h1><p>{error_msg}</p><p>Reason: {error_reason}</p>",
            status_code=400
        )


@router.get("/metadata")
async def saml_metadata(request: Request):
    """
    Service Provider metadata endpoint
    Okta can consume this to automatically configure the integration
    """
    req = prepare_fastapi_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    
    if len(errors) == 0:
        return HTMLResponse(content=metadata, media_type="application/xml")
    else:
        return HTMLResponse(
            content=f"<error>Error generating metadata: {', '.join(errors)}</error>",
            status_code=500,
            media_type="application/xml"
        )


@router.get("/sls")
async def saml_sls(request: Request):
    """Single Logout Service - handle logout requests from Okta"""
    req = prepare_fastapi_request(request)
    
    # Check if there's actually a SAML logout request/response
    if 'SAMLRequest' not in request.query_params and 'SAMLResponse' not in request.query_params:
        # No SAML logout in progress, just show logged out page
        root_path = request.scope.get("root_path", "")
        return templates.TemplateResponse("sls.html", {"request": request, "root_path": root_path})
    
    auth = init_saml_auth(req)
    
    try:
        url = auth.process_slo(delete_session_cb=lambda: None)
        errors = auth.get_errors()
        
        if len(errors) == 0:
            if url is not None:
                # Don't redirect if it's the same URL (prevents loop)
                if '/saml/sls' in url:
                    return templates.TemplateResponse("sls.html", {"request": request, "root_path": root_path})
                return RedirectResponse(url=url)
            else:
                return templates.TemplateResponse("sls.html", {"request": request, "root_path": root_path})
        else:
            return HTMLResponse(
                content=f"<h1>Logout Error</h1><p>{', '.join(errors)}</p><p><a href='/'>Home</a></p>",
                status_code=400
            )
    except Exception as e:
        # Don't fail on logout errors, just show success
        return HTMLResponse(
            content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Logged Out</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            max-width: 800px;
                            margin: 50px auto;
                            padding: 20px;
                            text-align: center;
                        }
                        .info {
                            background-color: #d1ecf1;
                            color: #0c5460;
                            padding: 15px;
                            border-radius: 5px;
                            margin: 20px 0;
                        }
                    </style>
                </head>
                <body>
                    <h1>✓ Logged Out</h1>
                    <div class="info">
                        Technically there was an issue, you have been logged out locally (SLS).
                    </div>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
            """
        )
