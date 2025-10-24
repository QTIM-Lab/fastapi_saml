"""
Main FastAPI application with SAML authentication
"""
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET_KEY
from routers import saml, protected, public


app = FastAPI(title="FastAPI SAML SSO Demo")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)


# Include routers
app.include_router(saml.router)
app.include_router(protected.router)
app.include_router(public.router)


if __name__ == "__main__":
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