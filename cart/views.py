from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST 
from django.forms.models import model_to_dict

from .cart import Cart
from shop.models import Food, Order, OrderItem
from user.models import Address
from user.forms import Addressform

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

@login_required
def checkout(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    form = Addressform()
    cart = Cart(request)

    if request.method == "POST":
        if id := request.POST.get("address_id"):
            address = get_object_or_404(Address, user=user, id=id)
            address_dict = model_to_dict(address, exclude=["id", "user", "full_name"])
            order = Order.objects.create(**address_dict, user=user,) # add paid=True after implementing payment logic

            for food in cart:
                OrderItem.objects.create(
                    order=order, food=food["food"], price=food["price"], 
                    quantity=food["quantity"],
                )

            # payment logic here
            
            messages.success(request, "Your Order has been Created")

            return redirect(reverse("index"))
        
        else:
            messages.error(request, "Pick an Address or Add one")

    context = {
        "addresses":addresses,
        "form":form,
    }

    return render(request, "cart/checkout.html", context)


@require_POST
def add_checkout_address(request):
    form = Addressform(request.POST)

    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()

        adrress_model = Address.objects.filter(user=request.user).values(
            "id", "first_name", "last_name",
            "full_name", "phone", "street", "city", "state", "country"
        )

        address_list = []
        for addr in adrress_model:
            addr["phone"] = str(addr["phone"].as_national)  # Make phone JSON-serializable
            address_list.append(addr)

        print(address_list)

        return JsonResponse({"success":True, "addresses":list(address_list)})
    
    else:
        return JsonResponse({"success":False, "errors":form.errors},)

def  delete_checkout_address(request, id):
    user = request.user
    address = get_object_or_404(Address, id=id, user=user)

    address.delete()

    adrress_model = Address.objects.filter(user=request.user).values(
        "id", "first_name", "last_name",
        "full_name", "phone", "street", "city", "state", "country"
    )

    address_list = []
    for addr in adrress_model:
        addr["phone"] = str(addr["phone"].as_national)  # Make phone JSON-serializable
        address_list.append(addr)

    return JsonResponse({"success":True, "addresses":list(address_list)})
    