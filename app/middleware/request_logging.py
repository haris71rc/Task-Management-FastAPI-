import logging,time
from uuid import uuid4
from fastapi import Request

logger = logging.getLogger(__name__)

async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid4())
    
    request.state.request_id = request_id
    
    start_time = time.perf_counter()
    
    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start_time
        
        logger.exception(
            "Request failed | "
            "request_id=%s | "
            "method=%s | "
            "path=%s | "
            "duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration * 1000,
        )
        
        raise
    
    duration = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    
    logger.info(
        "Request completed | "
        "request_id=%s | "
        "method=%s | "
        "path=%s | "
        "status_code=%s | "
        "duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration * 1000,
    )
    
    return response
        
    