import datetime
import logging
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

import uvicorn
from elasticsearch import Elasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from openai import AzureOpenAI, AsyncAzureOpenAI
from parliament.parlex_utils import parlex_query_eu_parliament
from pydantic import BaseModel
from utils.parlex_utils import filter_nones_from_stream


@lru_cache
def get_clients():
    es_client = Elasticsearch(
        cloud_id=os.environ.get("ELASTICSEARCH_CLOUD_ID"),
        api_key=os.environ.get("ELASTICSEARCH_API_KEY"),
    )
    openai_client = AsyncAzureOpenAI(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    )

    return {
        "es": es_client,
        "openai": openai_client,
    }


log = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    log.info("Starting up...")

    yield
    log.info("Shutting down...")


app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configure CORS

# origins = [settings.APP_URL]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(api_router, prefix="/api")


class ParlexSearchParams(BaseModel):
    user_query: str
    num_contributions: int
    month_range: list[datetime.date]


@app.post("/parlex/topic-search")
async def search_parlex_by_topic(
    params: ParlexSearchParams,
) -> StreamingResponse:
    clients = get_clients()
    return StreamingResponse(
        filter_nones_from_stream(
            parlex_query_eu_parliament(
                clients["es"],
                clients["openai"],
                params.user_query,
                params.month_range,
                params.num_contributions,
            )
        ),
        media_type="application/json",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
