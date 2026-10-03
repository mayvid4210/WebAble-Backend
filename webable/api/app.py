"""FastAPI application for the WebAble JSON API."""

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from webable.api.routes.analysis import router


def _development_origins() -> list[str]:
    configured_origins = os.getenv(
        "WEBABLE_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]


app = FastAPI(
    title="WebAble API",
    description="HTTP API for the WebAble accessibility audit engine.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_development_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def invalid_request_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    del request
    errors = error.errors()
    is_url_validation_error = any(
        "url" in entry.get("loc", ())
        for entry in errors
    )
    if is_url_validation_error:
        return JSONResponse(
            status_code=400,
            content={"detail": "Enter a valid HTTP or HTTPS URL."},
        )
    return JSONResponse(
        status_code=422,
        content={"detail": "The request body is invalid."},
    )


app.include_router(router, prefix="/api")
