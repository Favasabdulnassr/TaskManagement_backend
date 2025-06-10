from django.urls import path
from .views import RegisterView,VerifyOtpView,MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView




urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('verify-otp/',VerifyOtpView.as_view(),name='verify-otp'),
    path('token/',MyTokenObtainPairView.as_view(),name='token-login'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token-refresh')
    
]
