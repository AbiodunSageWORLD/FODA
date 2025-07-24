from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_summary, name = 'cart_summary'),
    path("checkout/", views.checkout, name = "checkout"),

    path("checkout/add-address/", views.add_checkout_address, name="add_checkout_address"),
    path("checkout/delete-address/<int:id>/", views.delete_checkout_address, name="delete_checkout_address"),

    path('add/<int:food_id>/', views.add_to_cart, name='cart_add'),
    path('delete/<int:food_id>/', views.cart_delete, name='cart_delete'),
    path('update/<int:food_id>/', views.cart_update, name='cart_update'),
]
