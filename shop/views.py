from django.shortcuts import render
from .models import Food
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