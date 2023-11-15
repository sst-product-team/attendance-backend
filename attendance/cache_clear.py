from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.urls import reverse


def home(request):
    if not request.user.is_staff:
        return JsonResponse(
            {"message": "You are not authorized to access this page", "status": "error"},
            status=403
        )
    
    url = reverse('clear_get_current_class')

    return render(request, 'cache.html', {'clear_url': url})


def clear_get_current_class(request):
    if not request.user.is_staff:
        return JsonResponse(
            {"message": "You are not authorized to access this page", "status": "error"},
            status=403
        )

    cache.delete('get_current_class')
    return JsonResponse({'message': 'Removed'})
