"""
Protected routes that require authentication
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from dependencies import require_auth

router = APIRouter(tags=["public"])


@router.get("/public")
async def test_public():
    """Public endpoint - no authentication required"""
    return {"message": "This is a public endpoint", "authentication": "not required"}


@router.get("/")
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
            <li><strong>GET /saml/logout</strong> - Initiate SSO logout</li>
            <li><strong>POST /saml/acs</strong> - Assertion Consumer Service (callback from Okta)</li>
            <li><strong>GET /saml/metadata</strong> - Service Provider metadata</li>
            <li><strong>GET /saml/sls</strong> - Single Logout Service</li>
            <li><strong>GET /protected</strong> - Example protected route</li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
