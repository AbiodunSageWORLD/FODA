from django.urls import path
from .views import vendor_dashboard
from . import views

urlpatterns = [
    path('dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path("open-hours/", views.vendor_business_hours, name="buisness_hours" ),
    path("foods/", views.vendor_food_list, name="vendor_food_list")
]
