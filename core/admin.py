from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import (
    CustomUser,
    Order,
    OrderProduct,
    Product,
    Store
)
# Register your models here.


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'password',
            'is_active',
            'is_staff',
            'is_store_owner',
            'first_name',
            'last_name'
        )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_store_owner',
        'date_created'
    )
    list_filter = ('is_store_owner',)

    fieldsets = (
        ('Credentials', {'fields': ('email', 'password')}),
        ('Personal information', {'fields': ('title', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_superuser', 'is_active', 'is_staff', 'is_store_owner')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'image',
        'store_type',
        'location',
        'store_owner'
    )
    list_filter = ('store_type',)
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'image',
        'brand_name',
        'size',
        'price',
        'quantity_on_stock',
        'product_type',
        'store'
    )
    list_filter = ('brand_name', 'product_type', 'store')
    search_fields = ('name', 'brand_name')


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'address',
        'postal_code',
        'city',
        'created',
        'updated',
        'paid',
    )
    list_filter = ('email', 'paid', 'city')
    search_fields = ('email',)
    inlines = [OrderProductInline]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.unregister(Group)