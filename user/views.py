from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout


from .forms import EditUserForm, Addressform
from .models import Address
from shop.models import Order

# Create your views here.
# you won a soul and stole a heart,evangelism is powerful
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        orders = request.user.order.all()[:5]
        addresses = request.user.address.all()[:5]

        context = {
            "orders":orders,
            "addresses": addresses
        }
        
        return render(request, "user/dashboard.html", context=context)
    

class EditUserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = EditUserForm(instance=user)

        context = {
            "form":form,
        }
        
        return render(request, "user/edit_user_profile.html", context=context)
    
    def post(self, request):
        user = request.user
        form = EditUserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()

            messages.success(request, "Your have successfully edited Your profile")

            return redirect(reverse("dashboard"))

        context = {
            "form":form,
        }
        
        return render(request, "user/edit_user_profile.html", context=context)
    

class DeleteUserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "user/delete_profile.html")

    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your have successfully deleted Your account")
        return redirect(reverse("index"))
    



class AddressView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "user/address_list.html"
    paginate_by = 5
    context_object_name = "addresses"
    ordering = "-id"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class AddAddressView(LoginRequiredMixin, View):
    def get(self, request):
        form = Addressform()

        context = {
            "form":form
        }

        return render(request, "user/add_address.html", context)

    def post(self, request):
        form = Addressform(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()

            messages.success(request, "New address has been added")

            return redirect(reverse("address_list"))

        context = {
            "form":form
        }

        return render(request, "user/add_address.html", context)


# Note: change Address.objects.get(pk=pk) so that it will relate directly
#  to the user in session, as of now another user can access another's address
#  by typing the link on the search bar directly
class EditAddressView(LoginRequiredMixin, View):
    def get(self, request, pk):
        model = get_object_or_404(Address, pk=pk, user=request.user)
        form = Addressform(instance=model)

        context = {
            "form":form
        }

        return render(request, "user/edit_address.html", context)

    def post(self, request, pk):
        model = Address.objects.get(pk=pk)
        form = Addressform(request.POST, instance=model)

        if form.is_valid():
            form.save()

            messages.success(request, "Your have succefully edited Your Address")

            return redirect(reverse("address_list"))

        context = {
            "form":form
        }

        return render(request, "user/edit_address.html", context)
    

class DeleteAddressView(LoginRequiredMixin, View):
    def get(self, request, pk):
        model = get_object_or_404(Address, pk=pk, user=request.user)
        model.delete()

        messages.success(request, "Your address has been deleted")

        return redirect(reverse("address_list"))
    

class OrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "user/orders_list.html"
    paginate_by = 5
    ordering = "-order_date"
    context_object_name = "orders"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    