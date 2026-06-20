from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/metrics")
def prometheus_metrics():
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return Response(
            content="# prometheus_client not installed\n",
            media_type="text/plain",
        )
