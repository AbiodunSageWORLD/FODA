from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
import json
from django.shortcuts import render, redirect
from .models import Vendor
from .utils import hash_password
from django.http import HttpResponse
from .utils import check_password
from shop.models import OrderItem, Food
from vendor.models import Vendor, BusinessHour
from .forms import BusinessHourFormSet


def v_signup(request):
    if request.method == "POST":
        
        email = request.POST["email"]
        password = request.POST["password"]

        if Vendor.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already taken"})

        hashed_pw = hash_password(password)
        Vendor.objects.create(email=email, password=hashed_pw)

        return redirect("v_login")

    return render(request, "v_signup.html")


def v_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = Vendor.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.id  # 🔑 store session
                return redirect("vendor_dashboard")
            else:
                return HttpResponse("Invalid password")
        except Vendor.DoesNotExist:
            return HttpResponse("User not found")

    return render(request, "v_login.html")

def logout(request):
    request.session.flush()
    return redirect("v_login")



# def is_vendor_user(user):
#     return user.is_authenticated and hasattr(user, 'vendor') and user.user_type == 'vendor'


# @login_required
# @user_passes_test(is_vendor_user, login_url='/auth/login/?next=/vendor-dashboard/')
def vendor_dashboard(request):
    if not request.vendor_user:
        return redirect("V_login")
   
    vendor = request.vendor_user

    # Food items created by the vendor
    vendor_foods = Food.objects.filter(vendor=vendor)
    
    total_foods = vendor_foods.count()

    # Total revenue and order items related to vendor
    order_items = OrderItem.objects.filter(vendor=vendor)

    total_sales = order_items.aggregate(
        total_revenue=Sum(F('quantity') * F('price'))
    )['total_revenue'] or 0

    # Sales by month
    sales_by_month = order_items.annotate(
        month=TruncMonth('order__order_date')
    ).values('month').annotate(
        total_sales=Sum(F('quantity') * F('price'))
    ).order_by('month')

    monthly_labels = [s['month'].strftime('%Y-%m') for s in sales_by_month]
    monthly_data = [float(s['total_sales']) for s in sales_by_month]

    # Sales by day (last 30 days)
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)

    sales_last_30_days = order_items.filter(
        order__order_date__gte=thirty_days_ago
    ).annotate(
        day=TruncDay('order__order_date')
    ).values('day').annotate(
        total_sales=Sum(F('quantity') * F('price'))
    ).order_by('day')

    daily_labels = [s['day'].strftime('%Y-%m-%d') for s in sales_last_30_days]
    daily_data = [float(s['total_sales']) for s in sales_last_30_days]

    # Top-selling foods
    top_selling_foods = order_items.values('food__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_quantity')[:5]

    context = {
        'vendor': vendor,
        'foods': vendor_foods,
        'orders': order_items,
        'total_foods': total_foods,
        'total_sales': total_sales,
        'sales_by_month_labels': json.dumps(monthly_labels),
        'sales_by_month_data': json.dumps(monthly_data),
        'sales_by_day_labels': json.dumps(daily_labels),
        'sales_by_day_data': json.dumps(daily_data),
        'top_selling_foods': top_selling_foods,
    }
    
    # return render(request, "dashboard.html", {"user": request.vendor_user})
    return render(request, "v_dashboard.html", context)


def vendor_business_hours(request):
    vendor = request.user.vendor
    business_hours = vendor.business_hour.all()

    if request.method == "POST":
        formset = BusinessHourFormSet(
            request.POST, request.FILES, instance=Vendor, queryset=business_hours
        )

        if formset.is_valid():
            formset.save()
            messages.success(request, "Schedule Updated Successfully!")
            return redirect(reverse())
    
    else:
        formset = BusinessHourFormSet(instance=Vendor, queryset=business_hours)

    context = {
        "business_hours":business_hours,
        "formset":formset
    }

    return render(request, "vendor/business_hours.html", context=context)
    
def vendor_food_list(request):
    vendor = request.user.vendor
    foods = Food.objects.filter(vendor=vendor)
    # foods = Food.objects.all()

    if request.method == "POST":
        id = request.POST.get("id","")
        operation = request.POST.get("method", "")
        
        try:
            # add vendor later
            food = Food.objects.get(id=id)
            name = food.name

            if operation == "true":
                food.is_sale = True
                food.save()
                return JsonResponse({"success":True, "message":f"{name} is now available in shop"})
            
            elif operation == "false":
                food.is_sale = False
                food.save()
                return JsonResponse({"success":True, "message":f"{name} has been removed from shop"})
            
            else:
                return JsonResponse(
                    {"success":False, "message":f"An error occured while updating {name} availability"}
                )

        except ObjectDoesNotExist:
            return JsonResponse({"success":False, "message":"The food does not exist, reload the page to fix error."})

    context = {
        "foods":foods
    }

    return render(request, "vendor/food_list.html", context=context)
