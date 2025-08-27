from shop.models import Food
from user.models import User
from decimal import Decimal


class Cart():
    def __init__(self, request):
    
        self.session = request.session
        self.request = request
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart  

    # loop through items in cart
    def __iter__(self):
        for food_id, detail in self.cart.items():
            food = Food.objects.get(id=food_id)
            price = detail.get("price")
            quantity = detail.get("quantity")
            total_price = float(price)*float(quantity)

            yield {"food":food, "price":price, "quantity":quantity, "total":total_price}

    def db_add(self, food, quantity):
        food_id = str(food.id)
        food_qty = int(quantity)

        if food_id not in self.cart:
            self.cart[food_id] = {
                'price': str(food.price),
                'quantity': food_qty
            }

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = User.objects.filter(id=self.request.user.id)
            carty = str(self.cart).replace("'", '"')  # Proper JSON-like format
            current_user.update(old_cart=carty)


    #Deal with logged in users

    def in_cart(self, food_id):
        return food_id in self.cart
       
    def add(self, food, quantity):
        food_id = str(food.id)
        food_qty = int(quantity)

        if food_id not in self.cart:
            self.cart[food_id] = {
                'price': str(food.price),
                'quantity': food_qty
            }

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = User.objects.filter(id=self.request.user.id)
            carty = str(self.cart).replace("'", '"')  # Proper JSON-like format
            current_user.update(old_cart=carty)
        
    def cart_total(self):
        food_ids = self.cart.keys()
        foods = Food.objects.filter(id__in=food_ids)

        total = Decimal('0.00')

        for food in foods:
            food_id = str(food.id)
            item = self.cart.get(food_id)

            # Safe check to skip bad entries
            if not isinstance(item, dict):
                continue

            quantity = item.get('quantity', 0)
            total += Decimal(item['price']) * quantity

        return total


    def __len__(self):
        return len(self.cart)
    

    def get_prods(self):
        food_ids = self.cart.keys()
        food = Food.objects.filter(id__in=food_ids)

        return food
    
    def get_quantities(self):
        quantities = self.cart
        return quantities
    

    def update(self, food, quantity):
        food_id = str(food.id)
        food_qty = int(quantity)

        if food_id in self.cart:
            self.cart[food_id] = {
                'price': str(food.price),
                'quantity': food_qty
            }  # ✅ Update quantity only

            if self.cart[food_id]["quantity"] == 0:
                self.delete(food_id)

            self.session.modified = True

            if self.request.user.is_authenticated:
                current_user = User.objects.filter(id=self.request.user.id)
                carty = str(self.cart).replace("'", '"')
                current_user.update(old_cart=carty)

        return self.cart

    
    
    
    
    def delete(self, food_id):
        food_id = str(food_id)
        if food_id in self.cart:
            del self.cart[food_id]
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = User.objects.filter(id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", '\"')

            current_user.update(old_cart=str(carty))
        return{
            'quantity': len(self.cart),
            'total_price': self.cart_total()
        }