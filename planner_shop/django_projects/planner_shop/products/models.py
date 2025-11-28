

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import os

def product_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.sku}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('products', 'images', filename)

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    PRODUCT_TYPES = [
        ('planner', 'Планинг'),
        ('sticker', 'Стикер'),
        ('kit', 'Набор'),
        ('accessory', 'Аксессуар'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, verbose_name="Тип товара")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Цена"

    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Скидка (%)"
    )

    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    stock_quantity = models.IntegerField(default=0, verbose_name="Количество на складе")
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"{self.title} ({self.sku})"
    
    def get_discounted_price(self):
        """Рассчитывает цену со скидкой"""
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price
    
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
