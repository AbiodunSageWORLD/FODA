from django.urls import path
from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),

    path("edit-profile/", views.EditUserProfileView.as_view(), name="edit_profile"),
    path("delete-profile/", views.DeleteUserProfileView.as_view(), name="delete_profile"),

    path("addresses/", views.AddressView.as_view(), name="address_list"),
    path("addresses/add-address/", views.AddAddressView.as_view(), name="add_address"),
    path("addresses/edit-address/<int:pk>", views.EditAddressView.as_view(), name="edit_address"),
    path("addresses/delete-address/<int:pk>", views.DeleteAddressView.as_view(), name="delete_address"),

   path("orders", views.OrderView.as_view(), name="order"), 
]
