# pages/views.py
from django.views.generic import TemplateView
from products.models import Product, Category, Brand, Banner

class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # دسته‌بندی‌های سطح ۱ (والدها)
        context["top_categories"] = Category.objects.filter(parent=None)[:8]

        # جدیدترین محصولات
        context["new_products"] = (
            Product.objects.filter(active=True)
            .order_by("-datetime_created")[:12]
        )

        # پرفروش‌ها
        context["best_sellers"] = (
            Product.objects.filter(active=True, is_best_seller=True)[:12]
        )

        # پیشنهاد ویژه
        context["special_offers"] = (
            Product.objects.filter(active=True, is_special_offer=True)[:8]
        )

        # برندها
        context["brands"] = Brand.objects.all()[:10]

        # بنرهای فعال (برای اسلایدر و تبلیغات)
        context["banners"] = Banner.objects.filter(فعال=True)

        return context
