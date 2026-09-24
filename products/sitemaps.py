from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(active=True).order_by('-datetime_modified')

    def lastmod(self, obj):
        return obj.datetime_modified


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ['pages:home', 'products:product_list']

    def location(self, item):
        return reverse(item)
