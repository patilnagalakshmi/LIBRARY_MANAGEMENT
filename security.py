import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from logger import setup_logger


logger = setup_logger('lib.log')
 
is_production = os.getenv("ENVIRONMENT") == "production"
 
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info("Processing request for path: %s", request.url.path)
        response: Response = await call_next(request)
        # Apply security headers only in production
        if not request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") :
            logger.info("Applying security headers.")
            if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline';"
                )
                logger.info("Applied CSP for docs: %s", response.headers["Content-Security-Policy"])
            else:
                response.headers["Content-Security-Policy"] = "default-src 'self';"
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
                response.headers["X-XSS-Protection"] = "0"  # Disable XSS protection
                response.headers["Referrer-Policy"] = "no-referrer"
 
                logger.info("Applied security headers: %s", response.headers)
 
        return response
