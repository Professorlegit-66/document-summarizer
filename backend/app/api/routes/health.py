from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Basic liveness check to confirm the API process is running."""
    return {"status": "ok"}