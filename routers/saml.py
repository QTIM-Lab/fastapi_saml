"""
SAML authentication routes
"""
import pdb
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from utils.saml_helpers import init_saml_auth, prepare_fastapi_request
from config import DEBUG

router = APIRouter(prefix="/saml", tags=["saml"])


@router.get("/validate")
async def validate(request: Request):
    """
    Endpoint for nginx auth_request
    Returns 200 if user is authenticated, 401 if not
    """
    # Check if session contains SAML authentication data
    saml_name_id = request.session.get('samlNameId')
    saml_userdata = request.session.get('samlUserdata')
    # pdb.set_trace()
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
    req = prepare_fastapi_request(request)
    auth = init_saml_auth(req)
    
    # Redirect to Okta for authentication
    sso_url = auth.login()
    return RedirectResponse(url=sso_url)


# Same as logout basically...merge
@router.get("/clear_session")
async def validate(request: Request):
    """
    Test endpoint to clear session
    """
    # pdb.set_trace()
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
    # In production, you'd clear the user's session here
    
    return HTMLResponse(content="""
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
                .success {
                    background-color: #d4edda;
                    color: #155724;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .info {
                    background-color: #d1ecf1;
                    color: #0c5460;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .button {
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 10px 5px;
                }
            </style>
        </head>
        <body>
            <h1>✓ Logged Out</h1>
            <div class="success">
                You have been logged out of this application.
            </div>
            <!--
            <div class="info">
                <p><strong>Note:</strong> You may still be logged into Okta.</p>
                <p>To completely log out of Okta, click the button below:</p>
                <a href="https://integrator-5479918.okta.com/login/signout" class="button" target="_blank">
                    Log Out of Okta
                </a>
            </div>
            -->
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
    """)



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
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Successful</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                }}
                .success {{
                    background-color: #d4edda;
                    color: #155724;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                pre {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                .button {{
                    background-color: #dc3545;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 10px 5px;
                }}
                .button-secondary {{
                    background-color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <h1>✓ Login Successful!</h1>
            <div class="success">
                <strong>You have successfully authenticated via Okta SAML SSO</strong>
            </div>
            
            <h3>User Information:</h3>
            <pre>{user_data}</pre>
            
            <p>
                <a href="/" class="button button-secondary">← Back to Home</a>
                <a href="/protected" class="button button-secondary">View Protected Page</a>
                <a href="/saml/logout" class="button">Logout from Okta</a>
            </p>
        </body>
        </html>
        """
        # pdb.set_trace()
        if DEBUG == 'True':
            return HTMLResponse(content=html_content)
        else:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>New Page Test</title>
                <style>
                </style>
            </head>
            <body>
                <h1>New Page Test!</h1>
            </body>
            </html>
            """
            # return HTMLResponse(content=html_content)

            return RedirectResponse(url='/protected', status_code=303)

            
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
        return HTMLResponse(content="""
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
                    You have been logged out successfully.
                </div>
                <p><a href="/">← Back to Home</a></p>
            </body>
            </html>
        """)
    
    auth = init_saml_auth(req)
    
    try:
        url = auth.process_slo(delete_session_cb=lambda: None)
        errors = auth.get_errors()
        
        if len(errors) == 0:
            if url is not None:
                # Don't redirect if it's the same URL (prevents loop)
                if '/saml/sls' in url:
                    return HTMLResponse(content="""
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
                                .success {
                                    background-color: #d4edda;
                                    color: #155724;
                                    padding: 15px;
                                    border-radius: 5px;
                                    margin: 20px 0;
                                }
                            </style>
                        </head>
                        <body>
                            <h1>✓ Logged Out Successfully</h1>
                            <div class="success">
                                You have been logged out from Okta.
                            </div>
                            <p><a href="/">← Back to Home</a></p>
                        </body>
                        </html>
                    """)
                return RedirectResponse(url=url)
            else:
                return HTMLResponse(content="""
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
                            .success {
                                background-color: #d4edda;
                                color: #155724;
                                padding: 15px;
                                border-radius: 5px;
                                margin: 20px 0;
                            }
                        </style>
                    </head>
                    <body>
                        <h1>✓ Logged Out Successfully</h1>
                        <div class="success">
                            You have been logged out.
                        </div>
                        <p><a href="/">← Back to Home</a></p>
                    </body>
                    </html>
                """)
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
                        You have been logged out locally.
                    </div>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
            """
        )
