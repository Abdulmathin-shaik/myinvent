from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .models import RawMaterial,Category,Transaction
from .forms import CategoryForm, RawMaterialForm, TransactionForm
from django.db import models
from django.db.models import F



# Create your views here.

def home(request):
    return render(request,'catalog/index.html')


def items(request):
    materials = RawMaterial.objects.all()
    return render(request,'catalog/item_list.html',{'material':materials})

def add_material(request):
    if request.method == 'POST':
        form = RawMaterialForm(request.POST)
        if form.is_valid():
            sku = form.cleaned_data['SKU']
            existing_material = RawMaterial.objects.filter(SKU=sku).first()
            if existing_material:
                # existing_material = RawMaterial.objects.filter(SKU=form.cleaned_data['SKU']).first()
                # existing_material.save()
                # messages.success(request, 'Material quantity updated successfully!')
                existing_material.quantity += form.cleaned_data['quantity']
                existing_material.save()
                messages.success(request, 'Material quantity updated successfully!')
            else:
                form.save()
                messages.success(request, 'Material added successfully!')
            return redirect('material_list')
    else:
        form = RawMaterialForm()
    return render(request, 'catalog/material_form.html', {'form': form})

# def delete_materials(request,pk):
#     material = RawMaterial.objects.get(pk=pk)
#     material.delete()
#     messages.success(request, 'Material deleted successfully!')
#     return redirect('material_list')

def transaction_history(request):
    transactions = Transaction.objects.all().order_by('-transaction_date')
    return render(request, 'catalog/transactions.html', {'transactions': transactions})

def low_stock_alerts(request):
    low_stock = RawMaterial.objects.filter(quantity__lte=models.F('reorder_level'))
    return render(request, 'catalog/alerts.html', {'low_stock': low_stock})

def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'catalog/categories.html', {'categories': categories})

def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, f'Transaction recorded successfully: {transaction}')
            return redirect('transaction_history')
    else:
        form = TransactionForm()
    return render(request, 'catalog/transaction_form.html', {'form': form})

def stock_in(request, material_id):
    material = get_object_or_404(RawMaterial, id=material_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        Transaction.objects.create(
            material=material,
            transaction_type="IN",
            quantity=quantity
        )
        messages.success(request, f'Added {quantity} units to {material.name}')
        return redirect('material_list')
    return render(request, 'catalog/stock_movement.html', {'material': material, 'action': 'in'})

def stock_out(request, material_id):
    material = get_object_or_404(RawMaterial, id=material_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        if quantity > material.quantity:
            messages.error(request, 'Insufficient stock!')
            return redirect('material_list')
        Transaction.objects.create(
            material=material,
            transaction_type="OUT",
            quantity=quantity
        )
        messages.success(request, f'Removed {quantity} units from {material.name}')
        return redirect('material_list')
    return render(request, 'catalog/stock_movement.html', {'material': material, 'action': 'out'})
