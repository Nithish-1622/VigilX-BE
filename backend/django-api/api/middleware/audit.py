import json
from django.utils.deprecation import MiddlewareMixin
from apps.audit.models import AuditLog

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to audit mutating API requests (POST, PUT, PATCH, DELETE) 
    and log security events like login attempts.
    """
    def process_response(self, request, response):
        # Only log requests directed to the REST APIs
        if not request.path.startswith('/api/'):
            return response

        # Only audit mutating methods (write operations) or authentication endpoints
        is_auth_endpoint = '/auth/' in request.path or '/login/' in request.path
        if request.method == 'GET' and not is_auth_endpoint:
            return response

        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user

        # Retrieve client IP Address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        action = f"{request.method} {request.path}"
        
        # Capture and sanitize body details
        details = {
            "status_code": response.status_code
        }
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Read request body content safely
            try:
                content_type = request.content_type or ''
                if 'application/json' in content_type and request.body:
                    body_data = json.loads(request.body.decode('utf-8'))
                    # Sanitize credentials/tokens from logs
                    for key in list(body_data.keys()):
                        key_lower = key.lower()
                        if any(secret_term in key_lower for secret_term in ['password', 'secret', 'token', 'refresh', 'access']):
                            body_data[key] = '********'
                    details['payload'] = body_data
            except Exception:
                details['payload_error'] = "Could not parse payload"

        # Special check: log login attempts where request.user is still Anonymous
        if is_auth_endpoint and 'login' in request.path and request.method == 'POST':
            try:
                body_data = json.loads(request.body.decode('utf-8'))
                details['attempted_username'] = body_data.get('username')
            except Exception:
                pass

        try:
            # Save audit log asynchronously / inline
            AuditLog.objects.create(
                user=user,
                action=action,
                ip_address=ip_address,
                details=details
            )
        except Exception:
            # Fail silently so we do not interrupt client requests if DB has write issues
            pass

        return response
