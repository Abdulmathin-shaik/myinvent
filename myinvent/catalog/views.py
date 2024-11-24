from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .models import RawMaterial,Category,Transaction, BillOfMaterials, BOMItem, ProductionOrder
from .forms import CategoryForm, RawMaterialForm, TransactionForm, BOMForm, BOMItemForm, ProductionOrderForm
from django.db import models
from django.db.models import F
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required



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
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'catalog/categories.html', {
        'categories': categories,
        'form': form
    })

def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'catalog/edit_category.html', {'form': form})

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('manage_categories')
    return render(request, 'catalog/delete_category.html', {'category': category})

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

@login_required
def dashboard(request): 
    # Get counts and summaries
    total_materials = RawMaterial.objects.count()
    low_stock_count = RawMaterial.objects.filter(quantity__lt=F('reorder_level')).count()
    active_orders = ProductionOrder.objects.filter(status='IN_PROGRESS').count()
    pending_orders = ProductionOrder.objects.filter(status='PENDING').count()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.all().order_by('-date')[:5]
    
    # Get low stock materials
    low_stock_materials = RawMaterial.objects.filter(
        quantity__lt=F('reorder_level')
    ).annotate(
        shortage=F('reorder_level') - F('quantity')
    )[:5]
    
    # Get order statistics for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    orders_by_status = ProductionOrder.objects.filter(
        created_date__gte=thirty_days_ago
    ).values('status').annotate(count=Count('id'))
    
    context = {
        'total_materials': total_materials,
        'low_stock_count': low_stock_count,
        'active_orders': active_orders,
        'pending_orders': pending_orders,
        'recent_transactions': recent_transactions,
        'low_stock_materials': low_stock_materials,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'catalog/dashboard.html', context)

def bom_list(request):
    boms = BillOfMaterials.objects.all()
    return render(request, 'catalog/bom_list.html', {'boms': boms})

def bom_detail(request, pk):
    bom = get_object_or_404(BillOfMaterials, pk=pk)
    items = bom.bomitem_set.all()
    
    if request.method == 'POST':
        form = BOMItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.bom = bom
            item.save()
            messages.success(request, f'Added {item.material.name} to BOM')
            return redirect('bom_detail', pk=pk)
    else:
        form = BOMItemForm()
    
    context = {
        'bom': bom,
        'items': items,
        'form': form,
        'total_cost': bom.get_total_cost()
    }
    return render(request, 'catalog/bom_detail.html', context)

def create_bom(request):
    if request.method == 'POST':
        form = BOMForm(request.POST)
        if form.is_valid():
            bom = form.save()
            messages.success(request, 'BOM created successfully')
            return redirect('bom_detail', pk=bom.pk)
    else:
        form = BOMForm()
    return render(request, 'catalog/bom_form.html', {'form': form})

def delete_bom_item(request, pk):
    item = get_object_or_404(BOMItem, pk=pk)
    bom_pk = item.bom.pk
    item.delete()
    messages.success(request, 'Material removed from BOM')
    return redirect('bom_detail', pk=bom_pk)

@login_required
def create_order(request):
    if request.method == 'POST':
        form = ProductionOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            action = request.POST.get('action')
            
            if action == 'start':
                order.status = 'PENDING'
                order.save()
                messages.success(request, 'Order created successfully. You can now start production.')
                return redirect('order_list')
            elif action == 'check':
                order.status = 'PENDING'
                order.save()
                return redirect('check_order', pk=order.pk)
    else:
        form = ProductionOrderForm()
    return render(request, 'catalog/order_form.html', {'form': form})

def update_order_status(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        old_status = order.status
        
        if new_status in dict(ProductionOrder.STATUS_CHOICES).keys():
            # If changing to IN_PROGRESS, deduct inventory
            if new_status == 'IN_PROGRESS' and old_status != 'IN_PROGRESS':
                if order.can_produce():
                    deduct_inventory(order)
                    order.status = new_status
                    order.save()
                    messages.success(request, 'Order status updated and inventory deducted.')
                else:
                    messages.error(request, 'Cannot start production: insufficient materials.')
                    return redirect('order_list')
            
            # If changing to CANCELLED, replenish inventory if it was IN_PROGRESS
            elif new_status == 'CANCELLED' and old_status == 'IN_PROGRESS':
                replenish_inventory(order)
                order.status = new_status
                order.save()
                messages.success(request, 'Order cancelled and inventory replenished.')
            
            # For other status changes
            else:
                order.status = new_status
                order.save()
                messages.success(request, 'Order status updated successfully.')
        
        else:
            messages.error(request, 'Invalid status selected.')
    return redirect('order_list')

def deduct_inventory(order):
    """Helper function to deduct inventory based on order"""
    for bom_item in order.bom.bomitem_set.all():
        material = bom_item.material
        required_qty = bom_item.quantity_required * order.quantity
        material.quantity -= required_qty
        material.save()
        
        # Record transaction
        Transaction.objects.create(
            material=material,
            transaction_type='OUT',
            quantity=required_qty,
            notes=f'Used in Production Order #{order.pk}'
        )

def replenish_inventory(order):
    """Helper function to replenish inventory when order is cancelled"""
    for bom_item in order.bom.bomitem_set.all():
        material = bom_item.material
        required_qty = bom_item.quantity_required * order.quantity
        material.quantity += required_qty
        material.save()
        
        # Record transaction
        Transaction.objects.create(
            material=material,
            transaction_type='IN',
            quantity=required_qty,
            notes=f'Replenished from cancelled Order #{order.pk}'
        )

def check_order(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    missing_materials = order.check_inventory()
    can_produce = order.can_produce()
    
    if request.method == 'POST' and can_produce:
        order.status = 'IN_PROGRESS'
        order.save()
        deduct_inventory(order)
        messages.success(request, 'Production started successfully!')
        return redirect('order_list')
    
    return render(request, 'catalog/check_order.html', {
        'order': order,
        'missing_materials': missing_materials,
        'can_produce': can_produce
    })

def order_list(request):
    orders = ProductionOrder.objects.all().order_by('-created_date')
    return render(request, 'catalog/order_list.html', {'orders': orders})

def scanner_view(request):
    return render(request, 'catalog/scanner.html')

def scan_material(request, barcode):
    try:
        material = RawMaterial.objects.get(barcode=barcode)
        return JsonResponse({
            'id': material.id,
            'name': material.name,
            'quantity': material.quantity,
        })
    except RawMaterial.DoesNotExist:
        return JsonResponse({'error': 'Material not found'}, status=404)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def material_detail(request, pk):
    material = get_object_or_404(RawMaterial, pk=pk)
    return render(request, 'catalog/material_detail.html', {'material': material})