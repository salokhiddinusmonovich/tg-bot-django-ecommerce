# Generated by Django 4.2 on 2024-11-04 19:02

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('bot_file', '0002_product'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creted date'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Published'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Names'),
        ),
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(upload_to='products/', verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.PositiveIntegerField(verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='bot_file.category', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_subcategory',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='product_category', chained_model_field='subcategory_category', null=True, on_delete=django.db.models.deletion.CASCADE, to='bot_file.subcategory', verbose_name='Subcategories'),
        ),
        migrations.AlterField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Edited date'),
        ),
    ]
