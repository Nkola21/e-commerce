from django.http import Http404
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext as _

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

class ProductListView(ListView):
    model = Product
    pk_url_kwarg = 'pk'
    template_name = 'core/product_list.html'

    def get(self, request, *args, **kwargs):
        store_id = kwargs.get('store_id', None)
        self.object_list = Product.objects.filter(store__id=store_id)
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        store = get_object_or_404(Store, id=store_id)
        stores = Store.objects.all()

        context = self.get_context_data()
        context['store'] = store
        context['stores'] = stores
        if request.user.is_authenticated:
            context['user'] = request.user
        return self.render_to_response(context)


def store_list(request):
    stores = get_list_or_404(Store)

    return render(
        request,
        'core/store_list.html',
        {'stores': stores}
    )


class ProductDetailView(DetailView):
    model = Product
    template_name = 'core/product_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        # self.pk_url_kwarg = kwargs.get('store_id')
        pk = self.kwargs.get('product_id')
        if pk is not None:
            queryset = Product.objects.filter(pk=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


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


class EditNewStoreView(UpdateView):
    model = Store
    queryset = Store.objects.all()
    success_url = '/'
    template_name = 'core/store_form.html'
    queryset = Store.objects.all()
    fields = [
        'store_owner',
        'store_type',
        'name',
        'location',
        'image'
    ]

    def get_object(self, queryset=None):
        # self.pk_url_kwarg = kwargs.get('store_id')
        pk = self.kwargs.get('store_id')
        if pk is not None:
            queryset = Store.objects.filter(pk=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class AddNewStoreView(CreateView):
    model = Store
    success_url = '/'
    fields = [
        'store_owner',
        'store_type',
        'name',
        'location',
        'image'
    ]

    # def post(self, request, **kwargs):
    #     form = self.get_form()
    #     form.files = request.FILES
    #     print(form)
    #     if form.is_valid():
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)