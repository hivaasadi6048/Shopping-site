import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from config import admin_access
from products.sitemaps import ProductSitemap, StaticViewSitemap

sitemaps = {
    'products': ProductSitemap,
    'static': StaticViewSitemap,
}

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

    path('__debug__/', include(debug_toolbar.urls)),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]  
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)