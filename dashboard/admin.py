from django.contrib import admin
from orders.models import Address, Order

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'city', 'address_line', 'phone_number')
    search_fields = ('title', 'user__username', 'city', 'address_line')