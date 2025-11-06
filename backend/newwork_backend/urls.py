"""
URL configuration for newwork_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenBlacklistView, )

# Customize the TokenObtainPairView to add schema tags
token_obtain_pair_view = extend_schema_view(
    post=extend_schema(tags=["Authentication"])
)(TokenObtainPairView.as_view())

token_refresh_view = extend_schema_view(
    post=extend_schema(tags=["Authentication"])
)(TokenRefreshView.as_view())

token_blacklist_view = extend_schema_view(
    post=extend_schema(tags=["Authentication"])
)(TokenBlacklistView.as_view())

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', token_obtain_pair_view, name='token_obtain_pair'),
    path('api/v1/token/refresh/', token_refresh_view, name='token_refresh'),
    path('api/v1/token/logout/', token_blacklist_view, name='token_logout'),
    path('api/v1/', include('hrapp.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
