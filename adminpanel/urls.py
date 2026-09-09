from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [

    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:id>/', views.product_delete, name='product_delete'),

    # سفارش‌ها
    path('orders/', views.order_list, name='order_list'),
    path('orders/status_update/<int:id>/', views.order_status_update, name='orders_status_update'),
    path('orders/update/<int:id>/', views.order_update, name='order_update'),
    path('orders/delete/<int:id>/', views.order_delete, name='order_delete'),

    # کامنت‌ها
    path('comments/', views.comment_list, name='comment_list'),
    path('comments/edit/<int:id>/', views.comment_edit, name='comment_edit'),
    path('comments/delete/<int:id>/', views.comment_delete, name='comment_delete'),
    path('comments/add/<int:product_id>/', views.add_comment, name='add_comment'),

    
        # برندها
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_add, name='brand_add'),
    path('brands/edit/<int:id>/', views.brand_edit, name='brand_edit'),
    path('brands/delete/<int:id>/', views.brand_delete, name='brand_delete'),

    # دسته‌بندی‌ها
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:id>/', views.category_delete, name='category_delete'),
    path("categories/save-tree/", views.save_category_tree, name="save_category_tree"),


        # تصاویر محصول
    path('products/<int:product_id>/images/', views.product_images_list, name='product_images_list'),
    path('products/<int:product_id>/images/add/', views.product_image_add, name='product_image_add'),
    path('products/images/edit/<int:id>/', views.product_image_edit, name='product_image_edit'),
    path('products/images/delete/<int:id>/', views.product_image_delete, name='product_image_delete'),

    # مشخصات فنی محصول
    path('products/<int:product_id>/specs/', views.product_specs_list, name='product_specs_list'),
    path('products/<int:product_id>/specs/add/', views.product_spec_add, name='product_spec_add'),
    path('products/specs/edit/<int:id>/', views.product_spec_edit, name='product_spec_edit'),
    path('products/specs/delete/<int:id>/', views.product_spec_delete, name='product_spec_delete'),

]