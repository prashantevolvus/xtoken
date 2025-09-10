#!/usr/bin/env python3
"""
FastAPI application for generating Superset guest tokens for embedding dashboards.

Usage:
  uvicorn main:app --reload

Env (.env):
  SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD,
  SUPERSET_LOGIN_PROVIDER, RLS_JSON, VERIFY_SSL
"""

import json
import os
from typing import List, Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn


# Load environment variables
load_dotenv()

# FastAPI app instance
app = FastAPI(
    title="Superset Guest Token Generator",
    description=(
        "API for generating Superset guest tokens for embedded dashboards"
    ),
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models


class GuestTokenRequest(BaseModel):
    dashboard: str = Field(
        ...,
        description="Dashboard UUID, numeric ID, or full dashboard URL"
    )
    username: Optional[str] = Field(
        "guest_via_api",
        description="Optional username for the guest token"
    )
    rls: Optional[List[dict]] = Field(
        default_factory=list,
        description="Row Level Security rules"
    )


class GuestTokenResponse(BaseModel):
    token: str
    dashboard_uuid: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: str

# Configuration


class Config:
    SUPERSET_URL = os.getenv("SUPERSET_URL")
    SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME")
    SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD")
    SUPERSET_LOGIN_PROVIDER = os.getenv("SUPERSET_LOGIN_PROVIDER", "db")
    VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() in {
        "1", "true", "yes", "y", "on"}
    RLS_JSON = os.getenv("RLS_JSON", "[]")

    @classmethod
    def validate(cls):
        if not cls.SUPERSET_URL or not cls.SUPERSET_USERNAME or not cls.SUPERSET_PASSWORD:
            raise HTTPException(
                status_code=500,
                detail="Missing environment variables. Set SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD in .env"
            )

        # Parse RLS as JSON array if it's a string
        if isinstance(cls.RLS_JSON, str):
            try:
                cls.RLS_JSON = json.loads(cls.RLS_JSON)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"RLS_JSON is not valid JSON: {e}"
                )

        if not isinstance(cls.RLS_JSON, list):
            raise HTTPException(
                status_code=500,
                detail="RLS_JSON must be a JSON array, e.g. [] or [{\"clause\":\"tenant_id='acme'\"}]"
            )

# Utility functions


def http_error_detail(resp: requests.Response) -> str:
    try:
        return resp.text
    except Exception:
        return f"status={resp.status_code}"


def login(session: requests.Session, base: str, username: str,
          password: str, provider: str, verify=True) -> str:
    r = session.post(
        f"{base}/api/v1/security/login",
        json={
            "username": username,
            "password": password,
            "provider": provider,
            "refresh": False},
        timeout=20,
        verify=verify,
    )
    if r.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Login failed ({r.status_code}): {http_error_detail(r)}"
        )
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Login succeeded but no access_token returned")
    return token


def get_csrf(session: requests.Session, base: str,
             access_token: str, verify=True) -> str:
    r = session.get(
        f"{base}/api/v1/security/csrf_token/",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
        verify=verify,
    )
    if r.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Fetching CSRF failed ({r.status_code}): {http_error_detail(r)}"
        )
    data = r.json()
    csrf = data.get("result")
    if not csrf:
        raise HTTPException(status_code=400,
                            detail="CSRF response missing 'result'")
    return csrf


def extract_candidate_from_url(dash_arg: str) -> str:
    """If a full URL is passed, return the last non-empty path segment."""
    try:
        p = urlparse(dash_arg)
        if p.scheme and p.netloc:
            parts = [seg for seg in p.path.split("/") if seg]
            if parts:
                return parts[-1]
    except Exception:
        pass
    return dash_arg


def resolve_dashboard_uuid(session: requests.Session, base: str,
                           access_token: str, dash_arg: str, verify=True) -> str:
    """
    Accepts:
      - UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) -> returns as-is
      - Numeric ID ("42")                            -> GET /api/v1/dashboard/42 to read 'uuid'
      - Full dashboard URL                           -> extracts last segment then applies above
    """
    candidate = extract_candidate_from_url(dash_arg).strip()

    # UUID heuristic
    if len(candidate) == 36 and candidate.count("-") == 4:
        return candidate

    # Assume numeric id
    r = session.get(
        f"{base}/api/v1/dashboard/{candidate}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
        verify=verify,
    )
    if r.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Could not resolve dashboard UUID from '{dash_arg}' ({r.status_code}): {http_error_detail(r)}"
        )
    data = r.json().get("result") or {}
    uuid = data.get("uuid")
    if not uuid:
        raise HTTPException(
            status_code=400,
            detail=f"Dashboard lookup returned no 'uuid' for '{dash_arg}'."
        )
    return uuid


def generate_guest_token(
    session: requests.Session,
    base: str,
    access_token: str,
    csrf_token: str,
    dashboard_uuid: str,
    rls: list,
    username: str = "guest_via_api",
    verify=True,
) -> str:
    payload = {
        "resources": [{"type": "dashboard", "id": dashboard_uuid}],
        "user": {"username": username},
        "rls": rls,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-CSRFToken": csrf_token,
        "Referer": base,
    }
    r = session.post(
        f"{base}/api/v1/security/guest_token/",
        json=payload,
        headers=headers,
        timeout=20,
        verify=verify,
    )
    if r.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"guest_token request failed ({r.status_code}): {http_error_detail(r)}"
        )
    data = r.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400,
                            detail="guest_token response missing 'token'")
    return token

# Dependency to validate configuration


def get_config():
    try:
        Config.validate()
        return Config
    except HTTPException:
        raise

# API endpoints


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Superset Guest Token Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.options("/generate-token")
async def options_generate_token():
    """Handle preflight CORS request"""
    return {"message": "OK"}


@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


@app.post("/generate-token", response_model=GuestTokenResponse)
async def generate_guest_token_endpoint(
    request: GuestTokenRequest,
    config: Config = Depends(get_config)
):
    """Generate a guest token for embedding a Superset dashboard"""
    try:
        # Trim trailing slash on base URL
        base = config.SUPERSET_URL[:-1] if config.SUPERSET_URL.endswith("/") else config.SUPERSET_URL

        # Use provided RLS or fall back to environment variable
        rls = request.rls if request.rls is not None else config.RLS_JSON

        with requests.Session() as session:
            # Login and get access token
            access_token = login(
                session, base, config.SUPERSET_USERNAME,
                config.SUPERSET_PASSWORD, config.SUPERSET_LOGIN_PROVIDER,
                verify=config.VERIFY_SSL
            )

            # Get CSRF token
            csrf_token = get_csrf(
                session,
                base,
                access_token,
                verify=config.VERIFY_SSL)

            # Resolve dashboard UUID
            dashboard_uuid = resolve_dashboard_uuid(
                session, base, access_token, request.dashboard,
                verify=config.VERIFY_SSL
            )

            # Generate guest token
            token = generate_guest_token(
                session, base, access_token, csrf_token,
                dashboard_uuid, rls, request.username, verify=config.VERIFY_SSL
            )

            return GuestTokenResponse(
                token=token,
                dashboard_uuid=dashboard_uuid,
                message="Guest token generated successfully"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/dashboard/{dashboard_id}", response_model=dict)
async def get_dashboard_info(
    dashboard_id: str,
    config: Config = Depends(get_config)
):
    """Get information about a specific dashboard"""
    try:
        base = config.SUPERSET_URL[:-1] if config.SUPERSET_URL.endswith("/") else config.SUPERSET_URL

        with requests.Session() as session:
            access_token = login(
                session, base, config.SUPERSET_USERNAME,
                config.SUPERSET_PASSWORD, config.SUPERSET_LOGIN_PROVIDER,
                verify=config.VERIFY_SSL
            )

            dashboard_uuid = resolve_dashboard_uuid(
                session, base, access_token, dashboard_id,
                verify=config.VERIFY_SSL
            )

            return {
                "dashboard_id": dashboard_id,
                "dashboard_uuid": dashboard_uuid,
                "message": "Dashboard UUID resolved successfully"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Error handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": "HTTP Error", "detail": exc.detail}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {"error": "Internal Server Error", "detail": str(exc)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
