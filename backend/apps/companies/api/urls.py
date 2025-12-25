from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CompanyThemeViewSet

router = DefaultRouter()
router.register(r'themes', CompanyThemeViewSet, basename='company-theme')

urlpatterns = [
    path('', include(router.urls)),
]
