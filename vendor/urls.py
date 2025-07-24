from django.urls import path
from .views import vendor_dashboard

urlpatterns = [
    path('dashboard/', vendor_dashboard, name='vendor_dashboard'),
]
