"""
Configuration settings for SAML authentication
"""
import os
from dotenv import load_dotenv
load_dotenv() 

sp_entityId = os.getenv("sp_entityId")
sp_assertionConsumerService = os.getenv("sp_assertionConsumerService")
sp_singleLogoutService = os.getenv("sp_singleLogoutService")
idp_entityId = os.getenv("idp_entityId")
idp_singleSignOnService = os.getenv("idp_singleSignOnService")
idp_singleLogoutService = os.getenv("idp_singleLogoutService")
idp_x509cert = os.getenv("idp_x509cert")
# import pdb; pdb.set_trace()

SESSION_SECRET_KEY = "your-secret-key-change-in-production"

SAML_SETTINGS = {
    "strict": False,  # Set to True in production
    "debug": True,
    "sp": {
        "entityId": sp_entityId,
        "assertionConsumerService": {
            "url": sp_assertionConsumerService,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": sp_singleLogoutService,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
        "x509cert": "",  # Optional: SP certificate
        "privateKey": ""  # Optional: SP private key
    },
    "idp": {
        # REPLACE THESE WITH YOUR OKTA VALUES
        "entityId": idp_entityId,
        "singleSignOnService": {
            "url": idp_singleSignOnService,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "singleLogoutService": {
            "url": idp_singleLogoutService,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": idp_x509cert  # Get from Okta
    }
}