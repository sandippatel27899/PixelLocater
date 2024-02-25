from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from imagesearch.views import LoginView, logout_user

urlpatterns = [
    path("", LoginView.as_view()),
    path("auth/logout/", logout_user, name="auth_logout" ),
    path('imagesearch/', include('imagesearch.urls')),
    path('admin/', admin.site.urls),
     
]

# Add this at the end of your urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
