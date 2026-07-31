"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from api.ai_views import AIAskV1View, AIAskV2View

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ai/ask", AIAskV1View.as_view(), name='root_ai_ask'),
    path("ai/v2/ask", AIAskV2View.as_view(), name='root_ai_v2_ask'),
    path("api/", include("api.urls")),
    path("", include("api.urls")),
]

# Serve media assets dynamically in local debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
