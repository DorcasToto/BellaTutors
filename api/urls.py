from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from api import views as api_views

urlpatterns = [
    path('login/', api_views.login, name='api_login'),
    path('get_user_handle/', api_views.get_user_handle, name='get_user_handle'),
    path('create_ticket/', api_views.create_ticket, name='create_ticket'),
    path('webhook/', api_views.webhook, name='webhook'),

]
if settings.DEBUG:
  urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
