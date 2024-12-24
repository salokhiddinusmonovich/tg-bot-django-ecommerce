from django.contrib import admin
from .models import Product, TelegramUser

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','created_at']
    list_display_links = ['id', 'name']
    search_fields = ['id', 'name', 'price']

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_login', 'registered_at', 'is_registered']
    list_display_links = ['id', 'user_login']
    search_fields = ['id', 'user_login', 'registered_at']
    readonly_fields = ['chat_id', 'user_login', 'user_password', 'is_registered']

