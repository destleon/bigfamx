from django.contrib import admin
from .models import Shop, Medicine, Sale, ShopAttendant

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'owner')
    search_fields = ('name', 'address', 'owner__username')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price', 'stock')
    list_filter = ('shop',)
    search_fields = ('name', 'description', 'shop__name')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'quantity', 'total_amount', 'shop', 'attendant', 'sale_date')
    list_filter = ('shop', 'sale_date')
    search_fields = ('medicine__name', 'shop__name', 'attendant__username')

@admin.register(ShopAttendant)
class ShopAttendantAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop')
    list_filter = ('shop',)
    search_fields = ('user__username', 'shop__name')