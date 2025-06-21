from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_summary, name = 'cart_summary'),
    path('add/<int:food_id>/', views.add_to_cart, name='cart_add'),
    path('delete/<int:food_id>/', views.cart_delete, name='cart_delete'),
    path('update/<int:food_id>/', views.cart_update, name='cart_update'),
]
