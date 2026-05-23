from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MasterViewSet, SketchViewSet, StyleViewSet, SketchViewSet, ClientViewSet, SessionViewSet

router = DefaultRouter()
router.register(r'masters', MasterViewSet, basename='master')
router.register(r'styes', StyleViewSet, basename='style')
router.register(r'sketch', SketchViewSet, basename='sketch')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'sessions', SessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]