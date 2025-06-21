from django.shortcuts import render, get_object_or_404
from .cart import Cart
from shop.models import Food
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.

def cart_summary(request):
    # cart = request.session.get('cart', {})
    # for key, value in cart.items():
    #     if isinstance(value, int):
    #         request.session['cart'] = {}  # Reset cart
    #         request.session.modified = True
    #         break 
    
    # Logic to retrieve cart items and total price
    cart = Cart(request)
    cart_food = cart.get_prods()
    quantities = cart.get_quantities()
    totals = cart.cart_total() 

    for food in cart_food:
        food_id = str(food.id)
        food.quantity = quantities.get(food_id, {}).get('quantity',0) 

    context = {
        'cart_items': cart_food,
        'total_price': totals

    }

    
    request.session.modified = True
    return render(request, 'cart_summary.html', context)

def add_to_cart(request, food_id):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        food_id = request.POST.get('food_item_id')
        food_qty = request.POST.get('food_item_qty')

        if not food_id or not food_qty or not food_qty.isdigit():
            return JsonResponse({'error': 'Invalid input'}, status=400)

        food_id = int(food_id)
        food_qty = int(food_qty)

        food = get_object_or_404(Food, id=food_id)
        cart.add(food=food, quantity=food_qty)

        cart_quantity = cart.__len__()

        messages.success(request, f'{food.name} has been added to your cart.')
        return JsonResponse({'cart_quantity': cart_quantity})


def cart_delete(request, food_id):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
    

        cart.delete(food_id=food_id)

        cart_quantity = len(cart)
        total_price = cart.cart_total()

        messages.success(request, 'Item has been removed from your cart.')
        return JsonResponse({'quantity': cart_quantity, 'total_price': total_price})


def cart_update(request, food_id):
    cart = Cart(request)
    food = Food.objects.get(id=food_id)
    food_qty = int(request.POST.get('quantity'))  # 🚨 Make sure this key matches your AJAX

    cart.update(food=food, quantity=food_qty)

    response = JsonResponse({'cart_quantity': len(cart)})
    return response


