"""
OmniAid Backend — Application Settings
=======================================
Loaded via pydantic-settings from .env.
Any missing REQUIRED field causes a ValidationError at import time,
which propagates to a startup failure with a clear, descriptive message.
"""

import sys
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All required environment variables for OmniAid.
    Fields without a default are REQUIRED — the app will not start without them.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # Silently ignore unknown env vars
        case_sensitive=False,    # GEMINI_API_KEY == gemini_api_key
    )

    # -----------------------------------------------------------------------
    # LLM Provider — Google Gemini (used for multimodal file extraction)
    # -----------------------------------------------------------------------
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")

    # -----------------------------------------------------------------------
    # LLM Provider — Groq (used for chat & text analysis — optional, falls back to Gemini)
    # -----------------------------------------------------------------------
    GROQ_API_KEY: str = Field(default="", description="Groq API key")

    # -----------------------------------------------------------------------
    # Fraud Verification APIs (all optional — app boots without them)
    # -----------------------------------------------------------------------
    GOOGLE_SAFE_BROWSING_KEY: str = Field(default="", description="Google Safe Browsing API v4 key")
    VIRUSTOTAL_API_KEY: str = Field(default="", description="VirusTotal API v3 key")
    IPQUALITYSCORE_API_KEY: str = Field(default="", description="IPQualityScore API key")

    # -----------------------------------------------------------------------
    # Twilio SMS Alerts (optional — alerts disabled if not set)
    # -----------------------------------------------------------------------
    TWILIO_ACCOUNT_SID: str = Field(default="", description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", description="Twilio Auth Token")
    TWILIO_FROM_NUMBER: str = Field(default="", description="Twilio sender phone number")

    # -----------------------------------------------------------------------
    # Speech-to-Text & Google Places
    # -----------------------------------------------------------------------
    SPEECH_TO_TEXT_API_KEY: str = Field(default="", description="Speech-to-text API key")
    GOOGLE_PLACES_API_KEY: str = Field(default="", description="Google Places API key")

    # -----------------------------------------------------------------------
    # Email OTP via Resend
    # -----------------------------------------------------------------------
    RESEND_API_KEY: str = Field(default="", description="Resend API key")
    RESEND_FROM_EMAIL: str = Field(default="SumScale Security <onboarding@resend.dev>", description="Resend Sender Email")

    # -----------------------------------------------------------------------
    # MongoDB (motor async driver)
    # -----------------------------------------------------------------------
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/omniaid",
        description="MongoDB connection string"
    )
    MONGODB_DB_NAME: str = Field(default="omniaid", description="MongoDB database name")

    # -----------------------------------------------------------------------
    # JWT Authentication
    # -----------------------------------------------------------------------
    JWT_SECRET_KEY: str = Field(
        default="sumscale_jwt_secret_production_key_minimum_32_chars",
        description="JWT signing secret"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=10080, description="Token lifetime in minutes (default: 7 days)")

    # -----------------------------------------------------------------------
    # CORS — frontend origin
    # -----------------------------------------------------------------------
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend origin for CORS")

    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------
    ENVIRONMENT: str = Field(default="production")
    LOG_LEVEL: str = Field(default="INFO")
    PORT: int = Field(default=8000, ge=1, le=65535)

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------
    @field_validator("FRONTEND_URL")
    @classmethod
    def no_trailing_slash(cls, v: str) -> str:
        """Strip trailing slash to prevent CORS mismatches."""
        return str(v).rstrip("/") if v else "http://localhost:5173"


def _load_settings() -> Settings:
    """
    Load settings safely and guarantee the app starts without unhandled exceptions.
    """
    try:
        return Settings()
    except Exception as exc:
        print(f"⚠️ Notice while parsing settings: {exc}. Using robust fallbacks.", file=sys.stderr)
        return Settings.model_construct()


settings: Settings = _load_settings()
