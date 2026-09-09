from django.contrib import admin
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.translation import gettext_lazy as _
from .models import (Banner,Product,Comment,Category,Brand,ProductImage,ProductSpecification,)


# ---------------------- INLINE MODELS ----------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text']
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ['name', 'value']
    verbose_name = "Specification"
    verbose_name_plural = "Specifications"


class CommentsInline(admin.TabularInline):
    model = Comment
    fields = ['author', 'body', 'stars', 'active']
    extra = 0
    verbose_name = "Comment"
    verbose_name_plural = "Comments"


# ---------------------- PRODUCT ADMIN ----------------------
@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'price', 'stock', 'stock_status', 'active','is_best_seller', ]
    list_filter = ['active', 'stock_status', 'brand', 'category','stock_status', 'active','is_best_seller',]
    search_fields = ['title', 'description', 'short_description']
    ordering = ['-datetime_created']
    list_editable = ['active', 'price', 'stock','stock_status', 'active','is_best_seller',]

    inlines = [
        ProductImageInline,
        ProductSpecificationInline,
        CommentsInline,
    ]

    fieldsets = (
        (_('Basic Info'), {
            'fields': ('title', 'short_description', 'description', 'image')
        }),
        (_('Category & Brand'), {
            'fields': ('category', 'brand')
        }),
        (_('Pricing & Stock'), {
            'fields': ('price', 'stock', 'stock_status', 'active')
        }),
        (_('Home Page Flags'), {  
            'fields': ('is_best_seller', 'is_special_offer', 'is_featured') 
        }),
        (_('Ownership & Dates'), {
            'fields': ('owner', 'datetime_created', 'datetime_modified')
        }),
    )
    readonly_fields = ['datetime_created', 'datetime_modified']


# ---------------------- CATEGORY ADMIN ----------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent', 'order']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['parent', 'order', 'title']

# ---------------------- BRAND ADMIN ----------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# ---------------------- COMMENT ADMIN ----------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'stars', 'active', 'datetime_created']
    list_filter = ['active', 'stars', 'datetime_created']
    search_fields = ['product__title', 'author__username', 'body']
    ordering = ['-datetime_created']




@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["عنوان", "فعال"]
    list_editable = ["فعال"]
