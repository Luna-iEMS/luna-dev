from fastapi import APIRouter
import platform, os, socket

router = APIRouter(prefix="/api/v1/system", tags=["System"])

@router.get("/info")
def system_info():
    """Liefert einfache System- und Versionsinformationen."""
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "release": platform.release(),
        "python_version": platform.python_version(),
        "container": os.getenv("HOSTNAME", "unknown"),
        "status": "ok"
    }
