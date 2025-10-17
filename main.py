from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import os


app = FastAPI()


# SAML Settings - Configure these based on your Okta setup
SAML_SETTINGS = {
    "strict": False,  # Set to True in production
    "debug": True,
    "sp": {
        "entityId": "http://localhost:8000/saml/metadata",
        "assertionConsumerService": {
            "url": "http://localhost:8000/saml/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": "http://localhost:8000/saml/sls",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
        "x509cert": "",  # Optional: SP certificate
        "privateKey": ""  # Optional: SP private key
    },
    "idp": {
        # REPLACE THESE WITH YOUR OKTA VALUES
        "entityId": "http://www.okta.com/exkwj0fq9kyTIwGPk697",
        "singleSignOnService": {
            "url": "https://integrator-5479918.okta.com/app/integrator-5479918_cuchatbot_1/exkwj0fq9kyTIwGPk697/sso/saml",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "singleLogoutService": {
            "url": "https://integrator-5479918.okta.com/app/integrator-5479918_cuchatbot_1/exkwj0fq9kyTIwGPk697/slo/saml",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": "MIIDtDCCApygAwIBAgIGAZnziCqcMA0GCSqGSIb3DQEBCwUAMIGaMQswCQYDVQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsGA1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxGzAZBgNVBAMMEmludGVncmF0b3ItNTQ3OTkxODEcMBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTAeFw0yNTEwMTcxODU1NTFaFw0zNTEwMTcxODU2NTFaMIGaMQswCQYDVQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsGA1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxGzAZBgNVBAMMEmludGVncmF0b3ItNTQ3OTkxODEcMBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKVvk58X3Oq5n8CuiKUxwdQuD5ZGhmVqDAWsWmv8wYniuwL016dXXqOVK78pyCQnE1/1ENtjRgqTruo+rRgXLGS5nsLNk8R5inbXM6c+V7uI9+ts24juCK0lqJgccA0cxpFt1QruwtdV0SXMhAYf2iUWnw73C4Qfvt5D2i8yPeQmRXRNaS2hOxDAWKSDxPTbDNIofdrkc7YWCup6Ockx9DrBD6e8frYm0wkeYi1i9eC8jzYmqcAIIkQ74xQgoutwZF+juqLr3e3HJOqH9YmCxCmFHdnMy0+trHb2HMSH8n1UQG7uccV3i54gT26HKcoUlODL3xOeVRfn3CUc9CO9fFcCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAIetb2wsWupZHI3xYUpbUEhUzFYyV5U/MNpAbuBRW2TfQbz9rHDq2eJndpvHfRAlbRYKi2zAfsgsaXUz20htsjDRzszCM6K9I9OlFJ4VOBuws27jLRuIcEkyV6lg3GD2K4/7TS2OZPcR31khmEmhMy1LknXOHVjF1aPiRKqchzcOad/paZ+VmN/OCmslHsBHIV2bmAiNCLyjIH/lG+nmHyQDLc/MyaOwloUE4q5H83XbfGCrOs7+bX0WJGLdHAPWiBkdZ1XZA4Y9BVG7cLo1AjzBbnSiJN0toQ8f7eWHe2UArVqGHi3eJH0e0DPDROrPLWoHB7Ma2c6962AiUmdX0uw=="  # Get from Okta
    }
}


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


@app.get("/")
async def home():
    """Home page with login link"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI SAML SSO Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .button {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
            }
            .info {
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #007bff;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>FastAPI SAML SSO with Okta</h1>
        <p>This is a demo application showing SAML Single Sign-On integration with Okta.</p>
        
        <div class="info">
            <strong>Setup Instructions:</strong>
            <ol>
                <li>Update SAML_SETTINGS in the code with your Okta values</li>
                <li>In Okta, set Single sign-on URL to: <code>http://localhost:8000/saml/acs</code></li>
                <li>In Okta, set Audience URI to: <code>http://localhost:8000/saml/metadata</code></li>
                <li>Click the login button below to test</li>
            </ol>
        </div>
        
        <a href="/saml/login" class="button">Login with Okta SSO</a>
        
        <h3>Available Endpoints:</h3>
        <ul>
            <li><strong>GET /saml/login</strong> - Initiate SSO login</li>
            <li><strong>POST /saml/acs</strong> - Assertion Consumer Service (callback from Okta)</li>
            <li><strong>GET /saml/metadata</strong> - Service Provider metadata</li>
            <li><strong>GET /saml/sls</strong> - Single Logout Service</li>
            <li><strong>GET /protected</strong> - Example protected route</li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/saml/login")
async def saml_login(request: Request):
    """Initiate SAML SSO login - redirects to Okta"""
    req = prepare_fastapi_request(request)
    auth = init_saml_auth(req)
    
    # Redirect to Okta for authentication
    sso_url = auth.login()
    return RedirectResponse(url=sso_url)


@app.post("/saml/acs")
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
            </style>
        </head>
        <body>
            <h1>✓ Login Successful!</h1>
            <div class="success">
                <strong>You have successfully authenticated via Okta SAML SSO</strong>
            </div>
            
            <h3>User Information:</h3>
            <pre>{user_data}</pre>
            
            <p><a href="/">← Back to Home</a> | <a href="/protected">View Protected Page</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        error_msg = ", ".join(errors)
        error_reason = auth.get_last_error_reason()
        return HTMLResponse(
            content=f"<h1>Error</h1><p>{error_msg}</p><p>Reason: {error_reason}</p>",
            status_code=400
        )


@app.get("/saml/metadata")
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


@app.get("/saml/sls")
async def saml_sls(request: Request):
    """Single Logout Service - handle logout requests from Okta"""
    req = prepare_fastapi_request(request)
    auth = init_saml_auth(req)
    
    url = auth.process_slo(delete_session_cb=lambda: None)
    errors = auth.get_errors()
    
    if len(errors) == 0:
        if url is not None:
            return RedirectResponse(url=url)
        else:
            return HTMLResponse(content="<h1>Logged out successfully</h1><p><a href='/'>Home</a></p>")
    else:
        return HTMLResponse(
            content=f"<h1>Logout Error</h1><p>{', '.join(errors)}</p>",
            status_code=400
        )


@app.get("/protected")
async def protected_route():
    """
    Example protected route
    In production, you'd check session/JWT here
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protected Page</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .protected {
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>🔒 Protected Page</h1>
        <div class="protected">
            <strong>Note:</strong> In a real application, this route would check if the user 
            has a valid session from SAML authentication. For this demo, it's accessible to all.
        </div>
        <p>This is a protected resource that should only be accessible after SAML authentication.</p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("FastAPI SAML SSO Server Starting...")
    print("="*60)
    print("\n📋 Setup Checklist:")
    print("   1. Update SAML_SETTINGS with your Okta configuration")
    print("   2. In Okta, set Single sign-on URL to:")
    print("      → http://localhost:8000/saml/acs")
    print("   3. In Okta, set Audience URI to:")
    print("      → http://localhost:8000/saml/metadata")
    print("\n🌐 Server running at: http://localhost:8000")
    print("   View metadata at: http://localhost:8000/saml/metadata")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)