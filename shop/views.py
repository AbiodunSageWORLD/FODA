from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

from .models import Food

from vendor.utils import get_current_day_and_time
from vendor.models import Vendor
from cart.cart import Cart
# Create your views here.




def index(request):
    context ={
         'mesage':'somethongS'
     }
    return render(request, 'index.html', context)


def shop(request):
    context = {
        'message': 'Welcome to the Food Delivery App!',
        'food_items': Food.objects.all()
    }
    return render(request, 'shop.html', context)

def food_detail(request, food_id):
    try:
        food_item = Food.objects.get(id=food_id)
    except Food.DoesNotExist:
        return render(request, '404.html', status=404)

    context = {
        'food_item': food_item
    }
    return render(request, 'detail.html', context)

def vendors_list(request):
    day, time = get_current_day_and_time()
    model = Vendor.objects.all()
    
    paginator = Paginator(model, 20)

    page_number = request.GET.get("page")

    try:
        vendors = paginator.get_page(page_number)
    except EmptyPage:
        vendors = paginator.get_page(paginator.num_pages)
    except InvalidPage:
        vendors = paginator.get_page(1)
    
    context = {
        "vendors":vendors
    }

    return render(request, "shop/vendors_list.html", context)

@csrf_exempt
def vendor_food_list(request, slug):
    day, time = get_current_day_and_time()
    vendor = get_object_or_404(Vendor, slug=slug)
    foods = vendor.foods.filter(is_sale=True)
    week_day = vendor.business_hour.filter(day=day).first()

    if request.method == "POST":
        cart = Cart(request)
        food_id = request.POST.get('food_id')
        food_qty = request.POST.get('quantity')
            
        food_id_int = int(food_id)
        food_qty = int(food_qty)

        food_cart = get_object_or_404(Food, id=food_id_int )

        if cart.in_cart(food_id):
            cart.update(food=food_cart, quantity=food_qty)

        else:
            cart.add(food=food_cart, quantity=food_qty)

        cart_quantity = cart.__len__()

        html = render_to_string("shop/includes/food_card.html", context={
            "foods":foods,
        }, request=request)

        return JsonResponse({'cart_quantity': cart_quantity, "html":html})

    context = {
        "vendor":vendor,
        "foods":foods,
        "week_day":week_day,
    }

    return render(request, "shop/vendor_food_list.html", context)

# @require_POST
# @csrf_exempt
# def add_remove_cart(request):
#     cart = Cart(request)
#     food_id = request.POST.get('food_id')
#     food_qty = request.POST.get('quantity')

#     if request.POST.get('action') == 'Add':
#         # if not food_id or not food_qty or not food_qty.isdigit():
#         #     return JsonResponse({'error': 'Invalid input'}, status=400)
        
#         food_id_int = int(food_id)
#         food_qty = int(food_qty)

#         food = get_object_or_404(Food, id=food_id_int )

#         if cart.in_cart(food_id):
#             cart.update(food=food, quantity=food_qty)

#         else:
#             cart.add(food=food, quantity=food_qty)

#         cart_quantity = cart.__len__()

#         html = render_to_string("shop/includes/food_card.html", context={}, request=request)

#         return JsonResponse({'cart_quantity': cart_quantity})