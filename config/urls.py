from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from config import admin_access

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminpanel/', include('adminpanel.urls', namespace='adminpanel')),
    path('', include('pages.urls', namespace='pages')),
    path('accounts/', include('accounts.urls')), 
    path('accounts/', include('allauth.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('orders.urls')),
    path("payment/", include("payment.urls", namespace="payment")),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    #آدرس پکیج ترجمه به فارسی روزتا
    path('rosetta/', include('rosetta.urls')),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)