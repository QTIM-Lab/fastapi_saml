"""
Main FastAPI application with SAML authentication
"""
import os
import pdb
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles


from config import SESSION_SECRET_KEY
from routers import saml, protected, public
from dotenv import load_dotenv


load_dotenv()
root_path = os.getenv("root_path")

app = FastAPI(title="FastAPI SAML SSO Demo", root_path=root_path)
app.add_middleware(SessionMiddleware,
                   secret_key=SESSION_SECRET_KEY,
                   same_site="lax",
                   https_only=False)

app.mount("/static", StaticFiles(directory="static"), name="static")


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