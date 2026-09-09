from django.contrib import admin
from .models import CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'datetime_created')
    list_filter = ('user',)
    search_fields = ('product__title', 'user__username')
