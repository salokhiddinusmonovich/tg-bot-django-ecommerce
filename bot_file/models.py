from django.db import models
from smart_selects.db_fields import ChainedForeignKey

class Product(models.Model):
    photo = models.ImageField(verbose_name='Images', upload_to='products/')
    name = models.CharField(verbose_name='Names', max_length=100)
    description = models.TextField(verbose_name='Description', blank=False)
    price = models.PositiveIntegerField(verbose_name='Price')
    created_at = models.DateTimeField(verbose_name='Created date', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Edited date', auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ['-created_at']


class TelegramUser(models.Model):
    chat_id = models.IntegerField(verbose_name='ID of user', unique=True, null=True)
    user_login = models.CharField(verbose_name='Login', max_length=255, unique=True)
    user_password = models.CharField(verbose_name='Password', max_length=128)
    is_registered = models.BooleanField(verbose_name='Registered', default=False)
    registered_at = models.DateTimeField(verbose_name='Registered time', auto_now_add=True)
    admin = models.BooleanField(default=False)  # Флаг администратора
    bought_products = models.ManyToManyField(Product, blank=True)
    comment = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user_login
    
    class Meta:
        verbose_name = 'Telegram user'
        verbose_name_plural = 'Telegram users'
        db_table = 'telegram_users'
        ordering = ['-registered_at']


class Promocode(models.Model):
    code = models.CharField(max_length=100, unique=True)  # Промокод
    promo_name = models.CharField(max_length=100)  # Название промокода
    reward = models.DecimalField(max_digits=10, decimal_places=2)  # Сумма вознаграждения для баланса
    who_have = models.ManyToManyField(TelegramUser, related_name='promocodes')  # Пользователи, у которых есть этот промокод

    def __str__(self):
        return self.code
