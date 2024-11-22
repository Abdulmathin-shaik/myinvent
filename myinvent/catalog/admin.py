from django.contrib import admin
from .models import RawMaterial,Category,Transaction

# Register your models here.

admin.site.register(RawMaterial)
admin.site.register(Category)
admin.site.register(Transaction)
