from django.shortcuts import render


# =============================================================================
# TODO: Replace With TemplateView
# =============================================================================

APP_NAME = 'pages'


def csrf_failure(request, reason=''):
    return render(request, f'{APP_NAME}/403csrf.html', status=403)


def page_not_found(request, exception=None):
    return render(request, f'{APP_NAME}/404.html', status=404)


def internal_server_error(request):
    return render(request, f'{APP_NAME}/500.html', status=500)
