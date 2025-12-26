from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyThemeViewSet,
    CompanyMemberListCreateView,
    CompanyMemberDetailView,
    CompanyMemberPasswordResetView,
)

router = DefaultRouter()
router.register(r'themes', CompanyThemeViewSet, basename='company-theme')

urlpatterns = [
    path('', include(router.urls)),
    path(
        '<uuid:company_uuid>/members/',
        CompanyMemberListCreateView.as_view(),
        name='company-members',
    ),
    path(
        '<uuid:company_uuid>/members/<uuid:member_uuid>/',
        CompanyMemberDetailView.as_view(),
        name='company-member-detail',
    ),
    path(
        '<uuid:company_uuid>/members/<uuid:member_uuid>/reset-password/',
        CompanyMemberPasswordResetView.as_view(),
        name='company-member-reset-password',
    ),
]
