from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout


from .forms import EditUserForm, Addressform
from .models import Address

# Create your views here.
# you won a soul and stole a heart,evangelism is powerful
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        orders = request.user.order.all()
        addresses = request.user.address.all()

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
    



class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "user/address_list.html")


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
        model = Address.objects.get(pk=pk)
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
        model = Address.objects.get(pk=pk)
        model.delete()

        messages.success(request, "Your address has been deleted")

        return redirect(reverse("address_list"))
    

class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        orders = request.user

        context = {
            "orders":orders,
        }
        
        return render(request, "user/orders_list.html", context=context)