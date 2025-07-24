from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta
from django.utils import timezone
import json

from shop.models import OrderItem, Food
from vendor.models import Vendor


def is_vendor_user(user):
    return user.is_authenticated and hasattr(user, 'vendor') and user.user_type == 'vendor'


@login_required
@user_passes_test(is_vendor_user, login_url='/auth/login/?next=/vendor-dashboard/')
def vendor_dashboard(request):
    vendor = request.user.vendor

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
        'total_foods': total_foods,
        'total_sales': total_sales,
        'sales_by_month_labels': json.dumps(monthly_labels),
        'sales_by_month_data': json.dumps(monthly_data),
        'sales_by_day_labels': json.dumps(daily_labels),
        'sales_by_day_data': json.dumps(daily_data),
        'top_selling_foods': top_selling_foods,
    }

    return render(request, 'templates/vendors_dashboard.html', context)
