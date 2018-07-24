from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .forms import (
    OrderCreateForm,
    ShoppingCartProductForm,
    SignUpForm
)
from .models import (
    CustomUser,
    ShoppingCart,
    Order,
    OrderProduct,
    Product,
    Store
)

@login_required
@require_POST
def cart_add(request, product_id):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, id=product_id)
    form = ShoppingCartProductForm(request.POST)
    if form.is_valid():
        clean_data = form.cleaned_data
        cart.add(
            product=product,
            quantity=clean_data['quantity'],
            update_quantity=clean_data['update']
        )
    return redirect('cart_detail', store_id=product.store_id)


@login_required
def cart_remove(request, product_id):
    cart = ShoppingCart(request)
    print("This product does exist: ", product_id)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    if cart.__len__() < 1:
        return redirect('product_list', store_id=product.store_id)
    return redirect('cart_detail', store_id=product.store_id)

@login_required
def cart_detail(request, store_id):
    cart = ShoppingCart(request)
    store = get_object_or_404(Store, id=store_id)
    for item in cart:
        item['update_quantity'] = ShoppingCartProductForm(
            initial={'quantity': item['quantity'], 'update': True}
        )
    return render(
        request,
        'core/cart_detail.html',
        {
            'cart': cart,
            'store': store
        }
    )


def product_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    stores = get_list_or_404(Store)
    products = get_list_or_404(Product, store=store)

    context = {
        'store': store,
        'stores': stores,
        'products': products
    }
    return render(
        request,
        'core/product_list.html',
        context
    )


def store_list(request):
    stores = get_list_or_404(Store)

    return render(
        request,
        'core/store_list.html',
        {'stores': stores}
    )


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    shopping_cart_form = ShoppingCartProductForm()
    context = {
        'product': product,
        'cart': shopping_cart_form
    }

    return render(
        request,
        'core/product_detail.html',
        context
    )

@login_required
def create_order(request):
    cart = ShoppingCart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        order = Order()
        if form.is_valid:
            if request.user.is_authenticated:
                user = CustomUser.objects.get(id=request.user.id)
                form.save(commit=False)
                form.customer = user
                order = form.save()
            else:
                order = form.save()
            for product in cart:
                OrderProduct.objects.create(
                    order=order,
                    product=product['product'],
                    quantity=product['quantity'],
                    price=product['price']
                )
            cart.clear()
        return render(request, 'core/created.html', {'order': order})
    else:
        form = OrderCreateForm()

    return render(
        request,
        'core/create.html',
        {
            'form': form,
            'cart': cart
        }
    )


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('stores')
    else:
        form = UserCreationForm()
    return render(request, 'core/sign_up.html', {'form': form})


def sign_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('stores')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})
