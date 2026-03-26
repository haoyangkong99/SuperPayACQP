"""
Header Cleanup Middleware
Removes unwanted headers from responses
"""


class HeaderCleanupMiddleware:
    """
    Removes unwanted headers from HTTP responses
    """
    
    # Headers to remove from responses
    HEADERS_TO_REMOVE = [
        'allow',
        'vary',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Remove unwanted headers
        for header in self.HEADERS_TO_REMOVE:
            if header in response.headers:
                del response.headers[header]
        
        return response
