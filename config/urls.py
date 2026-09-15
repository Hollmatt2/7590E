"""Maps web addresses to code. Each path() line sends one address to one view."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Django's built-in login and logout pages, at /accounts/login/ and /accounts/logout/.
    path('accounts/', include('django.contrib.auth.urls')),
    # Everything else belongs to our app. See core/urls.py.
    path('', include('core.urls')),
]
