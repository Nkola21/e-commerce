from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from core import views


urlpatterns = [
    path('', views.store_list, name='stores'),
    path('store/<int:store_id>/', views.ProductListView.as_view(), name='product-list'),
    path('store/<int:store_id>/update', views.EditNewStoreView.as_view(), name='store-edit'),
    path('product/<int:product_id>/update', views.EditProductView.as_view(), name='product-edit'),
    path('product/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('detail/<int:store_id>/', views.cart_detail, name='cart_detail'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('create_order/', views.create_order, name='create_order'),
    path('login/', views.sign_in, name='login_page'),
    path('logout/', auth_views.logout, {'next_page': 'login_page'}, name='logout'),
    path('sign_up/', views.sign_up, name='signup'),
    path('add_store/', views.AddNewStoreView.as_view(), name='new-store'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)