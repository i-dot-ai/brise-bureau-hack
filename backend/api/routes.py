import logging
from fastapi import APIRouter


from starlette.responses import JSONResponse


router = APIRouter()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/healthcheck")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.get("/info")
async def info():
    return {"backend": "FastAPI"}
