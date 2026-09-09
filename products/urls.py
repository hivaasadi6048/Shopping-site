from django.urls import path 
from .views import *

app_name = "products"

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('comment/<int:product_id>/', CommentCreateView.as_view(), name='comment_create'),
    path('category/<slug:slug>/',CategoryProductsView.as_view(), name='category_products'),
    path('brand/<slug:slug>/',BrandProductsView.as_view(),name='brand_products'),


]
