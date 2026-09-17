from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.storage import get_storage

router = APIRouter(tags=["media"])


@router.get("/media/{object_key:path}")
def media(object_key: str) -> Response:
    try:
        payload = get_storage().get_bytes(object_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid key")
    content_type = "image/jpeg" if object_key.endswith(".jpg") else "application/octet-stream"
    return Response(content=payload, media_type=content_type)
