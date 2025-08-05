from django.http import JsonResponse

class DisableLoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 302 and '/accounts/login/' in response.get('Location', ''):
            if request.path.startswith('/api/'):
                return JsonResponse({'detail': 'Authentication required'}, status=401)
        return response
