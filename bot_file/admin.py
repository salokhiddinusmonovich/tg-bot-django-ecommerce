from django.contrib import admin
from .models import Product, TelegramUser, Promocode

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'created_at']
    list_display_links = ['id', 'name']
    search_fields = ['id', 'name', 'price']

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_login', 'registered_at', 'is_registered']
    list_display_links = ['id', 'user_login']
    search_fields = ['id', 'user_login', 'registered_at']
    readonly_fields = ['chat_id', 'user_login', 'user_password', 'is_registered']

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'promo_name', 'reward', 'user_count']  # Make sure 'user_count' is correctly defined
    list_display_links = ['promo_name', 'code']
    search_fields = ['id', 'promo_name', 'code']
    readonly_fields = ['promo_name', 'code']

    def user_count(self, obj):
        return obj.who_have.count()  # Count the number of Telegram users who have this promocode
    user_count.short_description = 'Number of users'  # Custom label for the field

