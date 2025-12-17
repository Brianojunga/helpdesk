from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, TicketViewSet, RegisterViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'profiles', ProfileViewSet, basename='profiles')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'companies/<slug:slug>/tickets/',
        TicketViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='company-tickets'
    ),

    path(
        'companies/<slug:slug>/tickets/<int:pk>/',
        TicketViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'delete': 'destroy'
        }),
        name='company-ticket-detail'
    ),
]
