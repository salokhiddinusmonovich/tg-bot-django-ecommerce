from django.db import models
from smart_selects.db_fields import ChainedForeignKey

class TelegramUser(models.Model):
    chat_id = models.IntegerField(verbose_name='ID of user', unique=True, null=True)
    user_login = models.CharField(verbose_name='Login', max_length=255, unique=True)
    user_password = models.CharField(verbose_name='Password', max_length=128)
    is_registered = models.BooleanField(verbose_name='Registered', default=False)
    registered_at = models.DateTimeField(verbose_name='Registered time', auto_now_add=True)

    def __str__(self):
        return self.user_login
    
    class Meta:
        verbose_name = 'Telegram user'
        verbose_name_plural = 'Telegram users'
        db_table = 'telegram_users'
        ordering = ['-registered_at']


class Category(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    description = models.TextField(verbose_name='Описание', blank=True)
    created_at = models.DateTimeField(verbose_name='Время создания', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'categories'
        ordering = ['-created_at']

class Category(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100)
    description = models.TextField(verbose_name='Description', blank=True)
    created_at = models.DateTimeField(verbose_name='Creation Time', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'
        ordering = ['-created_at']


class SubCategory(models.Model):
    name = models.CharField(verbose_name='Subcategory Name', max_length=100)
    description = models.TextField(verbose_name='Subcategory Description', blank=True)
    created_at = models.DateTimeField(verbose_name='Subcategory Creation Time', auto_now_add=True)
    subcategory_category = models.ForeignKey(verbose_name='Category', to='Category', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'
        db_table = 'subcategories'
        ordering = ['-created_at']


class Product(models.Model):
    photo = models.ImageField(verbose_name='Images', upload_to='products/')
    name = models.CharField(verbose_name='Names', max_length=100)
    description = models.TextField(verbose_name='Description', blank=False)
    price = models.PositiveIntegerField(verbose_name='Price')
    created_at = models.DateTimeField(verbose_name='Creted date', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Edited date', auto_now=True)
    is_published = models.BooleanField(verbose_name='Published', default=True)
    product_category = models.ForeignKey(verbose_name='Category', to='Category', on_delete=models.PROTECT, null=True)

    # ChainedForeignKey Для работы с зависимыми полями (наша подкатегория зависима от категории). Smart Selects
    # Документация django-smart-selects https://django-smart-selects.readthedocs.io/en/latest/
    product_subcategory = ChainedForeignKey(
        to=SubCategory,
        chained_field='product_category',
        chained_model_field='subcategory_category',
        show_all=False,
        auto_choose=True,
        null=True,
        verbose_name='Subcategories'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ['-created_at']

