from django.urls import path
from . import views



    

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path('verify/', views.EmailAuthenticationView.as_view(), name='verify_email_page'),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    path("change-password/", views.UserPasswordChangeView.as_view(), name="change_password"),

    path("reset-password/", views.UserEmailPasswordResetView.as_view(), name="password_reset"),
    path("confirm-reset/<uidb64>/<token>", views.UserPasswordResetView.as_view(), name="confirm_reset"),
]
