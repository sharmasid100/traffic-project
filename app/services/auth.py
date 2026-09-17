from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials

from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
basic = HTTPBasic(auto_error=False)


def require_api_key(api_key: str | None = Depends(api_key_header)) -> None:
    settings = get_settings()
    if api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def require_dashboard(
    credentials: HTTPBasicCredentials | None = Depends(basic),
) -> str:
    settings = get_settings()
    if (
        credentials is None
        or credentials.username != settings.dashboard_user
        or credentials.password != settings.dashboard_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid dashboard credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
