from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.static import serve
from django.conf import settings

@login_required
def protected_media_serve(request, path):
    document_root = settings.MEDIA_ROOT
    try:
        return serve(request, path, document_root)
    except FileNotFoundError:
        raise Http404("File not found")
