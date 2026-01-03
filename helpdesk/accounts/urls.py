from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'profiles', ProfileViewSet, basename='profiles')

urlpatterns =[
    path('', include(router.urls)),
]