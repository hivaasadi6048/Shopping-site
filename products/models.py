from django.db import models
from django.conf import settings
from django.utils import timezone
from django.shortcuts import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from products.utils import sanitize_html


# ----------------------- CATEGORY -----------------------

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('عنوان دسته‌بندی'))
    slug = models.SlugField(unique=True, verbose_name=_('آدرس وب'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('دسته‌بندی والد')
        
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('دسته‌بندی')
        verbose_name_plural = _('دسته‌بندی‌ها')
        ordering = ['order','title']

    def clean(self):
        # اگر هنوز ذخیره نشده (id ندارد)، از بخش self-parent عبور کن
        if self.pk and self.parent_id == self.pk:
            # فقط وقتی چک کن که هم خودت id داری هم parent تنظیم شده
            raise ValidationError(_("یک دسته نمی‌تواند والد خودش باشد."))

        # جلوگیری از حلقه‌های چندسطحی
        parent = self.parent
        # اینجا نیازی نیست self.pk داشته باشه، فقط اگر parent تنظیم شده بررسی می‌کنیم
        visited = set()
        while parent is not None:
            if parent.pk == self.pk and self.pk is not None:
                # یعنی در زنجیرهٔ والدها دوباره به خودت رسیدی
                raise ValidationError(_("ساختار دسته‌بندی باعث ایجاد حلقه می‌شود."))
            # برای اطمینان از عدم چرخش عجیب
            if parent.pk in visited:
                raise ValidationError(_("ساختار دسته‌بندی نامعتبر است (حلقه‌ای)."))
            visited.add(parent.pk)
            parent = parent.parent

    def save(self, *args, **kwargs):
        # تولید خودکار slug اگر خالی باشد
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        # اجرای محافظ قبل از ذخیره
        self.clean()

        super().save(*args, **kwargs)

    def __str__(self):
        full_path = [self.title]
        parent = self.parent
        while parent is not None:
            full_path.append(parent.title)
            parent = parent.parent
        return ' / '.join(full_path[::-1])


# ----------------------- BRAND -----------------------
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('نام برند'))
    slug = models.SlugField(unique=True, blank=True, null=True)
    logo = models.ImageField(upload_to='product/brands/', blank=True, null=True, verbose_name=_('لوگو'))
    description = models.TextField(blank=True, verbose_name=_('توضیحات'))

    class Meta:
        verbose_name = _('برند')
        verbose_name_plural = _('برندها')
        ordering = ['name']

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        # تولید خودکار slug از نام برند اگر پر نشده باشد
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ----------------------- PRODUCT -----------------------
class Product(models.Model):
    STOCK_STATUS = (
        ('in_stock', _('موجود')),
        ('out_of_stock', _('ناموجود')),
        ('pre_order', _('پیش‌سفارش')),
    )

    title = models.CharField(max_length=200, verbose_name=_('نام محصول'))
    description = CKEditor5Field(config_name='default', verbose_name=_('توضیحات'))
    short_description = models.TextField(blank=True, verbose_name=_('توضیحات کوتاه'))
    price = models.PositiveIntegerField(default=0, verbose_name=_('قیمت'))
    stock = models.PositiveIntegerField(default=0, verbose_name=_('موجودی'))
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS, default='in_stock', verbose_name=_('وضعیت موجودی'))
    active = models.BooleanField(default=True, verbose_name=_('فعال'))
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('تاریخ ایجاد'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ تغییر'))
    image = models.ImageField(upload_to='product/product_cover/', blank=True, verbose_name=_('تصویر اصلی'))
    is_best_seller = models.BooleanField(default=False, verbose_name=_('پرفروش‌ترین'))
    is_special_offer = models.BooleanField(default=False, verbose_name=_('پیشنهاد ویژه'))
    is_featured = models.BooleanField(default=False, verbose_name=_('مخصوص صفحه اصلی'))

    sales_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد فروش'))

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Owner"),
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_('دسته‌بندی')
    )
    brand = models.ForeignKey(
        'Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_('برند')
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"pk": self.pk})
   

    def save(self, *args, **kwargs):
        self.description = sanitize_html(self.description)
        super().save(*args, **kwargs)
    
    
# ----------------------- MULTIPLE IMAGES -----------------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('محصول'))
    image = models.ImageField(upload_to='product/gallery/', verbose_name=_('تصویر'))
    alt_text = models.CharField(max_length=150, blank=True, verbose_name=_('متن جایگزین'))

    class Meta:
        verbose_name = _('تصویر محصول')
        verbose_name_plural = _('تصاویر محصول')

    def __str__(self):
        return f"{self.product.title} - Image"


# ----------------------- SPECIFICATIONS -----------------------
class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications', verbose_name=_('محصول'))
    name = models.CharField(max_length=100, verbose_name=_('نام ویژگی'))
    value = models.CharField(max_length=255, verbose_name=_('مقدار ویژگی'))

    class Meta:
        verbose_name = _('ویژگی')
        verbose_name_plural = _('ویژگی‌ها')

    def __str__(self):
        return f"{self.product.title} - {self.name}: {self.value}"


# ----------------------- COMMENTS -----------------------
class ActiveCommentsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Comment(models.Model):
    PRODUCT_STARS = [
        ('1', 'خیلی بد'),
        ('2', 'بد'),
        ('3', 'متوسط'),
        ('4', 'خوب'),
        ('5', 'عالی'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name=_('محصول'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('نویسنده')
    )
    body = CKEditor5Field(config_name='default', verbose_name=_('متن نظر'))
    stars = models.CharField(max_length=10, choices=PRODUCT_STARS, verbose_name=_('امتیاز'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ تغییر'))
    active = models.BooleanField(default=False, verbose_name=_('فعال'))

    objects = models.Manager()
    active_comments = ActiveCommentsManager()

    def __str__(self):
        return f"{self.author} - {self.product.title}"

    def get_absolute_url(self):
        return reverse("products:product_detail", args={self.product.id})


    def save(self, *args, **kwargs):
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)



class Banner(models.Model):
    عنوان = models.CharField(max_length=200, verbose_name="عنوان بنر")
    تصویر = models.ImageField(upload_to="banners/", verbose_name="تصویر")
    لینک = models.URLField(blank=True, null=True, verbose_name="لینک مقصد")
    فعال = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"

    def __str__(self):
        return self.عنوان
