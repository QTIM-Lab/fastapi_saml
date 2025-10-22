
# FastAPI and SAML Integration

## FastAPI
```bash
pyenv activate fastapi_saml
poetry init
```

```bash
cp .env_sample .env # fill in
fastapi dev main.py # dev
python main.py # prod
```

## SAML Workflow
![saml_guidance_saml_flow.png](saml_guidance_saml_flow.png)

## Project layout
```bash
fastapi_saml/
├── main.py                # Entry point, app initialization
├── dependencies.py        # Shared dependencies (like require_auth)
├── config.py              # Configuration (SAML_SETTINGS, etc.)
├── routers/
│   ├── __init__.py
│   ├── saml.py            # All SAML routes
│   ├── protected.py       # Protected routes
│   └── public.py          # Public routes (if you have many)
└── utils/
    ├── __init__.py
    └── saml_helpers.py    # SAML helper functions
```