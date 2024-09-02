from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('custom_account/', include('custom_account.urls')),
    path('custom_account/', include('django.contrib.auth.urls')),
    path('custom_account/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('cart/', include('cart.urls')),
    path('chat/', include('chat_app.urls')),
    path("", include('admin_corporate.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
