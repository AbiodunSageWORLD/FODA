from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('shop', views.shop, name = 'shop'),
    path('food/<int:food_id>/', views.food_detail, name='detail'),
    path("resturant/", views.vendors_list, name="vendors_list"),
    path("resturant/<slug:slug>/", views.vendor_food_list, name="vendor_foods_list")
]
