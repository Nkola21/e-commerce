from decimal import Decimal

from django.db import models
from django.conf import settings
from django.contrib.auth.models  import AbstractBaseUser, PermissionsMixin
from django.shortcuts import get_list_or_404

from .user_manager import UserManager
# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    titles = (
        ('MR','Mr.'),
        ('MISS','Miss'),
        ('MRS', 'Mrs.')
    )
    title = models.CharField(max_length=9, choices=titles, blank=True)
    first_name = models.CharField(max_length=15, blank=True)
    last_name = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=25,unique=True)
    is_store_owner = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    objects = UserManager()

    def str(self):
        return f'{first_name} {last_name}'

    def get_fullname(self):
        return f'{first_name} {last_name}'


class Store(models.Model):
    STORE_TYPE = (
        ('CLOTHING', 'Clothing'),
        ('HOME', 'HOME'),
        ('FURNITURE', 'Furniture'),
        ('ELECTRONIC_DEVICE', 'Electronic Device'),
    )
    name = models.CharField(max_length=25)
    image = models.ImageField(upload_to=settings.UPLOAD_DIR, max_length=500)
    store_type = models.CharField(max_length=25, choices=STORE_TYPE, blank=True)
    location = models.CharField(max_length=50, blank=True)
    store_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def set_store_owner(self, store_owner):
        if CustomUser.objects.filter(email=store_owner.email).exists:
            self.store_owner = store_owner
        else:
            raise ValueError('User does not exists.')

class Product(models.Model):
    PROD_TYPE = (
        ('CLOTHING', 'Clothing'),
        ('HOME', 'HOME'),
        ('FURNITURE', 'Furniture'),
        ('ELECTRONIC_DEVICE', 'Electronic Device')
    )

    name = models.CharField(max_length=25)
    image = models.ImageField(upload_to=settings.UPLOAD_DIR)
    brand_name = models.CharField(max_length=25)
    size = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_on_stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    product_type = models.CharField(max_length=25, choices=PROD_TYPE, blank=True)
    store = models.ForeignKey(Store, related_name='Store',on_delete=models.CASCADE)

    def __str__(self):
        return self.brand_name

    def set_quantity(self, quantity):
        self.quantity_on_stock = quantity

    def get_quantity(self):
        return self.quantity_on_stock


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)



class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product,  on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return '{}'.format(self.id)

    def cost(self):
        return self.price * self.quantity


class ShoppingCart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.SESSION_ID)
        if not cart:
            cart = self.session[settings.SESSION_ID] = {}
        self.cart = cart

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = get_list_or_404(Product, id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                      'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session[settings.SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        self.session[settings.SESSION_ID] = {}
        self.session.modified = True

    def get_total_price(self):
        print("Method has been called")
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())