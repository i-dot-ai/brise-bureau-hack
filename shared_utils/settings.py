import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
import streamlit as st
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_PORT: int = os.environ.get("API_PORT", 8080)
    BACKEND_URL: str = "http://localhost:8080"
    APP_URL: str
    APP_NAME: str = os.environ.get("APP_NAME")
    AWS_REGION: str
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT")
    SENTRY_DSN: Optional[str] = None
    openai_api_version: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment_name: Optional[str] = None
    azure_openai_embed_endpoint: Optional[str] = None
    azure_openai_embed_model: Optional[str] = None
    azure_openai_embed_api_key: Optional[str] = None
    elasticsearch_api_key: Optional[str] = None
    elasticsearch_endpoint: Optional[str] = None
    elasticsearch_cloud_id: Optional[str] = None
    backend_host: Optional[str] = None

    openai_api_version: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment_name: Optional[str] = None

    azure_openai_embed_endpoint: Optional[str] = None
    azure_openai_embed_model: Optional[str] = None
    azure_openai_embed_api_key: Optional[str] = None

    elasticsearch_api_key: Optional[str] = None
    elasticsearch_endpoint: Optional[str] = None
    elasticsearch_cloud_id: Optional[str] = None

    backend_host: Optional[str] = None

    # if ENVIRONMENT == "local":
    #     model_config = SettingsConfigDict(env_file=".env")
