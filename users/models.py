from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, default="")
    details = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="item_images/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    color_variant = models.CharField(max_length=100, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title