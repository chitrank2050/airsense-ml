"""
Monitoring endpoints for AirSense ML API.

Exposes drift detection reports comparing production prediction
distribution against training reference data.

Endpoints:
    GET /v1/monitoring/report — generate and return drift report
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.monitoring import DriftReportResponse
from api.utils.rate_limit import limiter
from src.core.logger import logger
from src.db.connection import get_db
from src.monitoring.drift import generate_drift_report

router = APIRouter()


@router.get(
    "/monitoring/report",
    response_model=DriftReportResponse,
    summary="Generate data drift report",
    description=(
        "Compares recent production predictions against training data distribution. "
        "Requires at least 10 production predictions in the database."
    ),
)
@limiter.limit("10/minute")
async def drift_report(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> DriftReportResponse:
    """Generate Evidently drift report.

    Args:
        request: FastAPI Request format for rate limiting.
        db: Database session — injected by FastAPI.

    Returns:
        DriftReportResponse with drift summary.

    Raises:
        HTTPException: 400 if insufficient production data.
        HTTPException: 500 if report generation fails.
    """
    try:
        result = await generate_drift_report(db)
        return DriftReportResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Drift report failed: {e}")
        raise HTTPException(
            status_code=500, detail="Drift report generation failed."
        ) from e
