from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.api.v1.views import UserResource, LoginAPIView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserResource, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginAPIView.as_view(), name='login'),
]
