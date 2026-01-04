from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  TicketViewSet, CompanyViewSet, TicketResolutionViewset

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(
    r'companies/(?P<slug>[^/.]+)/ticket-resolution', 
    TicketResolutionViewset, 
    basename='ticket-resolution'
    )
router.register(
    r'companies/(?P<slug>[^/.]+)/tickets',
    TicketViewSet,
    basename='company-tickets'
)


urlpatterns = [
    path('', include(router.urls))
]
