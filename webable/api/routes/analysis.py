"""Analysis and health endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from webable.analysis import analyze_website
from webable.api.schemas import (
    AnalysisRequest,
    AnalyzeResponse,
    AuditReportResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalysisRequest) -> AnalyzeResponse:
    try:
        report = analyze_website(request.url)
    except PlaywrightTimeoutError as error:
        logger.warning("Website scan timed out for %s: %s", request.url, error)
        raise HTTPException(
            status_code=504,
            detail="The website took too long to respond.",
        ) from error
    except PlaywrightError as error:
        logger.warning("Browser scan failed for %s: %s", request.url, error)
        raise HTTPException(
            status_code=502,
            detail="The website could not be loaded for analysis.",
        ) from error
    except Exception as error:
        logger.exception("Unexpected analysis failure for %s", request.url)
        raise HTTPException(
            status_code=500,
            detail="The analysis could not be completed.",
        ) from error

    return AnalyzeResponse(
        report=AuditReportResponse.from_audit_report(report),
    )
