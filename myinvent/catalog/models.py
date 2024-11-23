from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'


class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    SKU = models.CharField(max_length=50,unique=False) #changed it to false 
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True) #for foriegn key two required arguments - linking model and on_delete
    quantity = models.IntegerField()
    location = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)
    reorder_level = models.IntegerField(validators = [MinValueValidator(0)])
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f" {self.name} - {self.SKU}"
    
    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.material.name} ({self.quantity})"

    def save(self,*args,**kwargs):
        if self.transaction_type == "IN":
            self.material.quantity += self.quantity
        else:
            self.material.quantity -= self.quantity
        self.material.save()
        super().save(*args,**kwargs)


    class Meta:
        ordering = ['-date']


class BillOfMaterials(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_total_cost(self):
        total = sum(item.get_cost() for item in self.bomitem_set.all())
        return round(total, 2)

class BOMItem(models.Model):
    bom = models.ForeignKey(BillOfMaterials, related_name='bomitem_set', on_delete=models.CASCADE)
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.material.name} - {self.quantity_required}"
    
    def get_cost(self):
        return self.quantity_required * self.material.cost  # You'll need to add a cost field to RawMaterial


class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def check_inventory(self):
        missing_materials = []
        for bom_item in self.bom.bomitem_set.all():
            required_qty = bom_item.quantity_required * self.quantity
            available_qty = bom_item.material.quantity
            
            if available_qty < required_qty:
                missing_materials.append({
                    'material': bom_item.material.name,
                    'required': required_qty,
                    'available': available_qty,
                    'shortage': required_qty - available_qty
                })
        return missing_materials

    def can_produce(self):
        return len(self.check_inventory()) == 0




 




    