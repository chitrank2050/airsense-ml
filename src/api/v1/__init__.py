"""
Version 1 API router.

Aggregates all v1 endpoint routers into a single router that app.py
mounts under the /v1 prefix. Adding a new endpoint module means
importing its router here and including it — nothing else changes.

Responsibility: assemble v1 routes. Nothing else.
Does NOT: define endpoints, handle requests, or manage application state.
"""

from fastapi import APIRouter

from src.api.v1 import health, model_info, monitoring, predict

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(model_info.router, tags=["Model"])
router.include_router(predict.router, tags=["Predictions"])
router.include_router(monitoring.router, tags=["Monitoring"])

__all__ = ["router"]
