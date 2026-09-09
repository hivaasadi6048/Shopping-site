from django.views import generic
from django.db.models import Q
from .models import Product, Comment, Category, Brand 
from .forms import CommentForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Min, Max


class ProductListView(generic.ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(active=True)

        query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        brand_slug = self.request.GET.get('brand')
        special = self.request.GET.get('special_offer')
        best = self.request.GET.get('best_seller')
        order = self.request.GET.get('order')
        sort = self.request.GET.get('sort')  # اضافه شد
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')

        # ✅ فیلتر دسته‌بندی (شامل زیرمجموعه‌ها)
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                category_ids = [category.id] + list(category.children.values_list("id", flat=True))
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                queryset = queryset.none()

        # ✅ فیلتر برند
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)

        # ✅ فیلتر قیمت
        try:
            if price_min:
                queryset = queryset.filter(price__gte=int(price_min))
            if price_max:
                queryset = queryset.filter(price__lte=int(price_max))
        except ValueError:
            pass

        # ✅ پیشنهاد ویژه
        if special:
            queryset = queryset.filter(is_special_offer=True)

        # ✅ پرفروش‌ها (برچسب)
        if best:
            queryset = queryset.filter(is_best_seller=True)

        # ✅ مرتب‌سازی جدیدترین‌ها
        if order == "new":
            queryset = queryset.order_by("-datetime_created")

        # ✅ مرتب‌سازی سفارشی (ارزان‌ترین، گران‌ترین، پرفروش‌ترین)
        if sort == "cheap":
            queryset = queryset.order_by("price")
        elif sort == "expensive":
            queryset = queryset.order_by("-price")
        elif sort == "popular":
            # بدون تغییر مدل: بر اساس برچسب پرفروش + تاریخ
            queryset = queryset.order_by("-is_best_seller", "-datetime_created")

        elif sort == "new": queryset = queryset.order_by("-datetime_created")
        
        # ✅ سرچ پیشرفته
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(short_description__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(category__title__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context['query'] = request.GET.get('q', '')
        context['sort'] = request.GET.get('sort', '')
        context['brands'] = Brand.objects.all().order_by('name')

        # برای بردکرامب
        category_slug = request.GET.get('category')
        context['current_category'] = None
        if category_slug:
            context['current_category'] = Category.objects.filter(slug=category_slug).first()

        
        
        price_range = Product.objects.filter(
            active=True
        ).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )

        context['min_price'] = price_range['min_price'] or 0
        context['max_price'] = price_range['max_price'] or 0
        
        return context




class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = context.get('form', CommentForm())
        return context
    



class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):

        # دریافت محصول
        product_id = int(self.kwargs['product_id'])
        product = get_object_or_404(Product, id=product_id)

        # بررسی آخرین کامنت کاربر
        last_comment = (
            Comment.objects
            .filter(author=self.request.user)
            .order_by('-datetime_created')
            .first()
        )

        if last_comment:
            delta = timezone.now() - last_comment.datetime_created

            if delta.total_seconds() < 30:
                messages.error(
                    self.request,
                    "لطفاً قبل از ارسال کامنت بعدی کمی صبر کنید."
                )

                # بازگشت امن به صفحه محصول
                return redirect(product.get_absolute_url())

        # ذخیره کامنت
        form.instance.author = self.request.user
        form.instance.product = product

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.product.get_absolute_url()
    
    
    


class CategoryProductsView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(
            active=True,
            category__slug=self.kwargs["slug"]
        )


class BrandProductsView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(
            active=True,
            brand__slug=self.kwargs["slug"]
        )