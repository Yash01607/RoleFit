from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime

from app.models.schema.fastapi.error_detail import ErrorDetail
from app.models.schema.fastapi.standard_response import StandardResponse


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                StandardResponse(
                    data=None,
                    error=ErrorDetail(
                        timestamp=datetime.utcnow(),
                        status_code=exc.status_code,
                        detail=str(exc.detail),
                        endpoint=str(request.url),
                    ),
                )
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                StandardResponse(
                    data=None,
                    error=ErrorDetail(
                        timestamp=datetime.utcnow(),
                        status_code=422,
                        detail=str(exc),
                        endpoint=str(request.url),
                    ),
                )
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                StandardResponse(
                    data=None,
                    error=ErrorDetail(
                        timestamp=datetime.utcnow(),
                        status_code=500,
                        detail=str(exc),
                        endpoint=str(request.url),
                    ),
                )
            ),
        )
