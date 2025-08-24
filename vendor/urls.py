from django.urls import path
from . import views

urlpatterns = [
    path('v_signup/', views.v_signup, name='vendor_signup'),
    path('v_login/', views.v_login, name='vendor_login'),
    path('v_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path("open-hours/", views.vendor_business_hours, name="buisness_hours" ),
    path("foods/", views.vendor_food_list, name="vendor_food_list")
]
