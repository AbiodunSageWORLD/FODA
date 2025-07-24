from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


from user.models import User
from .forms import SignUpForm, LoginForm

from axes.models import AccessAttempt


# TBD - NAME OF THE TEMPLATES AND REDIRECTS


class SignUpView(View):
    def get(self, request):
        form = SignUpForm

        context = {
            "form":form
        }

        return render(request, "auth/signup.html", context=context)
        

    def post(self, request):
        form = SignUpForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")

            user = form.save()

            user.generate_verification_code()

            # check user model for email generation code 

            messages.success(request, "Check your email for the confirmation Code")

            # redirects user to authentication page
            return redirect(reverse("verify_email_page"))
        
        context = {
            "form":form
        }

        return render(request, "auth/signup.html", context=context)
        



class LoginView(View):
    def get(self, request):
        form = LoginForm()

        next_url = request.GET.get("next", "")

        context = {
            "form":form,
            "next":next_url
        }

        return render(request, "auth/login.html", context=context)
        

    def post(self, request):
        form = LoginForm(request, request.POST)
        next_url= request.POST.get("next", "")
        email = request.POST.get("username", "")

        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=email, password=password)

            if user != None:
                # NOte to self, test this error that come from this in the login html
                if user.is_active:
                    login(request, user) 

                    # redirects to previous page the user was in instead of home page
                    if next_url != "":
                        return redirect(next_url)

                    return redirect(reverse("dashboard"))

                else:
                    messages.error(request, "Your account is not active. " \
                    "Please check your email for the verification link or code.")
                    
                    return redirect(reverse("verify_email_page"))
                
        # check how many times an email has attempted login
        if email:
            login_attempt = AccessAttempt.objects.get(username=email
                                                # for more specific tracking, also used by IP:
                                                # ip_address = get_client_ip(request)  
                                                ).failures_since_start 
        
        context = {
            "form":form,
            "next":next_url,
            "login_attempt":login_attempt,
        }

        return render(request, "auth/login.html", context=context)
        

class EmailAuthenticationView(View):
    def get(self, request):
        return render(request, "auth/email_code_verification.html")
    
    def post(self, request):
        code = request.POST.get("verification_code","")

        try:
            user = User.objects.get(verification_code=code, is_active=False) 

            if not user.is_verification_code_valid():
                messages.error(request, "The verification code is invalid or has expired. Please request a new one.")
                return render(request, "auth/email_code_verification.html") 

            user.activate() 

            messages.success(request, "Your account has been successfully activated! You are now logged in.")

            login(request, user)

            return redirect(reverse("dashboard")) 

        except User.DoesNotExist:
            messages.error(request, "The verification code is invalid or has expired. Please request a new one.")
            return render(request, "auth/email_code_verification.html")


class RefreshCodeEmailAuthenticationView(View):
    def post(self, request):
        email = request.POST.get("email")

        try:
            validate_email = EmailValidator()

            if validate_email(email):
                user = get_object_or_404(User, email=email)

                if user:
                    user.generate_verification_code()


        except ValidationError as e:
            return JsonResponse({"status":"Error", "message":e.message})

        return JsonResponse({"status":"Success", "message":"New confirmation Code has been sent"})
        

class LogoutView(View):
    def get(self, request):
        logout(request)

        #back to homepage
        return redirect()


class UserEmailPasswordResetView(SuccessMessageMixin, PasswordResetView):
    email_template_name = "auth/email_password_reset.html"
    template_name = "auth/confirm_email_password_reset.html"
    success_url = reverse_lazy("login")
    success_message = "We have  emailed you instructions for resetting your password" \
                    "If an account exists with the email you entered. You should recieve them shortly" \
                    "If you don't recieve an email," \
                    "please make sure you have entered the address registered with, and checked your spam folder"

class UserPasswordResetView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = "auth/reset_password.html"
    success_url = reverse_lazy("login")
    success_message = "Your password has been set.  You may go ahead and log in now."

class UserPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = "auth/password_change.html"
    success_url = reverse_lazy("dashboard")
    success_message = "Your password was changed."
