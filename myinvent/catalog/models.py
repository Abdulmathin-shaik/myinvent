from django.db import models
from django.core.validators import MinValueValidator

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


    def __str__(self):
        return f" {self.name} - {self.SKU}"
    
    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class Transaction(models.Model):
    Transaction_types = [
        ("IN","Stock in"),
        ("OUT","Stock out")
    ]
    material =  models.ForeignKey(RawMaterial,on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3,choices=Transaction_types)
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.transaction_type} - {self.material.name} - {self.quantity}"

    def save(self,*args,**kwargs):
        if self.transaction_type == "IN":
            self.material.quantity += self.quantity
        else:
            self.material.quantity -= self.quantity
        self.material.save()
        super().save(*args,**kwargs)


    class Meta:
        ordering = ['-transaction_date']




 




    