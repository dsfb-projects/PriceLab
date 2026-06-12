from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from app.views import upload_base, resultados_latest, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', login_view),
    path('api/upload/', upload_base),
    path('api/resultados/', resultados_latest),
    path('', TemplateView.as_view(template_name='index.html')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
