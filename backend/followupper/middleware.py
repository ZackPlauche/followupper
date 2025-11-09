"""
Request logging middleware for Django.
"""
import json
import time
from django.utils.deprecation import MiddlewareMixin


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all incoming requests with details."""
    
    def process_request(self, request):
        """Log request details."""
        request.start_time = time.time()
        
        body = None
        if hasattr(request, 'body') and request.body:
            try:
                body = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = request.body.decode('utf-8', errors='ignore')
        
        print(f"\n{'='*60}")
        print(f"🌐 {request.method} {request.path}")
        if body:
            print(f"📦 Body: {json.dumps(body, indent=2) if isinstance(body, dict) else body}")
        print(f"{'='*60}\n")
    
    def process_response(self, request, response):
        """Log response details."""
        duration = time.time() - request.start_time if hasattr(request, 'start_time') else 0
        print(f"✅ {request.method} {request.path} - {response.status_code} ({duration:.3f}s)\n")
        return response

