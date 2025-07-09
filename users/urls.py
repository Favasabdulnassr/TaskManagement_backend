from django.urls import path
from .views import RegisterView,VerifyOtpView,MyTokenObtainPairView,ProfileUpdateView,ResendOtpView
from rest_framework_simplejwt.views import TokenRefreshView




urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('resend-otp/',ResendOtpView.as_view(),name='resend-otp'),
    path('verify-otp/',VerifyOtpView.as_view(),name='verify-otp'),
    path('token/',MyTokenObtainPairView.as_view(),name='token-login'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),
    path('profile/update/',ProfileUpdateView.as_view(),name='profile-update')
    
]
