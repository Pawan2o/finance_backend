
from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView
from api.ForgetPassword.view import PasswordResetConfirmView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('pass-reset/<str:temp_token>/', PasswordResetConfirmView.as_view(), name='pass-reset'),
]
